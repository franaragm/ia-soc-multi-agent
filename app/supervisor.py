from app.services.llm_client import llm_chain_openai
from langgraph_supervisor import create_supervisor
from agents import alert_analyzer, threat_analyzer, notification_agent
from datetime import datetime
import json

# Inicializa el modelo LLM que será usado por el supervisor
llm = llm_chain_openai()


def build_soc_workflow():
    """
    Construye y compila el workflow principal del SOC basado en arquitectura multiagente.

    Este método:
    - Define un supervisor central usando LangGraph
    - Orquesta la ejecución secuencial de 3 agentes especializados:
        1. alert_analyzer → análisis de IOCs
        2. threat_analyzer → evaluación de amenaza (condicional)
        3. notification_agent → envío de notificación
    - Aplica reglas estrictas de flujo (máximo 3 pasos, sin loops)

    Returns:
        Compiled workflow listo para ser invocado (.invoke())
    """

    # Crear el supervisor multiagente
    supervisor = create_supervisor(
        agents=[alert_analyzer, threat_analyzer, notification_agent],
        model=llm,
        prompt="""Eres el supervisor del SOC que coordina EXACTAMENTE 3 pasos secuenciales.

        AGENTES DISPONIBLES:
        1. **alert_analyzer**: Analiza IOCs y determina VERDADERO/FALSO POSITIVO
        2. **threat_analyzer**: Evalúa severidad y propone mitigación (solo para verdaderos positivos)  
        3. **notification_agent**: Envía email final con resultados

        FLUJO OBLIGATORIO - NO DESVIAR:
        1. PASO 1: Delegar a "alert_analyzer" para análisis inicial
        2. PASO 2: Si VERDADERO POSITIVO → "threat_analyzer" | Si FALSO POSITIVO → saltar a paso 3
        3. PASO 3: Delegar a "notification_agent" para envío final
        4. FINALIZAR: Cuando notification_agent complete, TERMINAR inmediatamente

        REGLAS CRÍTICAS:
        - NO HACER análisis propio - solo coordinar agentes
        - NUNCA volver a un agente ya ejecutado
        - TERMINAR después del notification_agent
        - NO continuar después de enviar email
        - Máximo 3 delegaciones por alerta
        """,
        add_handoff_back_messages=True,
        output_mode="full_history"
    )

    # Compila el workflow para ejecución eficiente
    return supervisor.compile()


# Instancia global reutilizable del workflow SOC
soc_workflow = build_soc_workflow()


def process_security_alert(alert_data: dict, incident_id: str, processing_context: dict = None) -> dict:
    """
    Procesa una alerta de seguridad completa utilizando el workflow multiagente.

    Este método:
    - Construye el input inicial para el supervisor
    - Ejecuta el flujo completo de análisis (alert → threat → notification)
    - Extrae los resultados de cada agente desde el historial
    - Devuelve un objeto estructurado con resultados SOC

    Args:
        alert_data (dict): Datos crudos de la alerta (logs, eventos, IOCs, etc.)
        incident_id (str): Identificador único del incidente
        processing_context (dict, optional): Contexto adicional (email destino, metadata, etc.)

    Returns:
        dict: Resultado completo del procesamiento incluyendo:
            - análisis de alerta
            - evaluación de amenaza
            - estado de notificación
            - herramientas utilizadas
            - historial completo de ejecución
    """

    if processing_context is None:
        processing_context = {}

    # Construir mensaje inicial que guía al supervisor
    initial_message = f"""
    ALERTA SOC PARA PROCESAMIENTO SECUENCIAL:

        ID: {incident_id}
        DATOS: {json.dumps(alert_data, indent=2)}
        EMAIL: {processing_context.get('email_recipient', 'engineer.education.colab@gmail.com')}

        INSTRUCCIÓN CLARA: Ejecutar EXACTAMENTE estos 3 pasos:
        1. alert_analyzer → análisis IOCs y determinar VERDADERO/FALSO POSITIVO
        2. SI verdadero positivo → threat_analyzer → evaluación severidad y mitigación  
        3. notification_agent → envío email final

        TERMINAR después del paso 3. NO continuar.
    """

    print(f"🚀 Iniciando arquitectura supervisor para {incident_id}")
    print("🤖 Flujo: alert_analyzer → threat_analyzer → notification_agent")

    try:
        # Ejecutar el workflow multiagente
        result = soc_workflow.invoke({
            "messages": [{"role": "user", "content": initial_message}]
        })

        # Extraer resultados de cada agente desde el historial
        analysis_result = _extract_agent_result(result, "alert_analyzer")
        threat_result = _extract_agent_result(result, "threat_analyzer")
        notification_result = _extract_agent_result(result, "notification_agent")

        # Detectar herramientas utilizadas (para auditoría SOC)
        tools_used = ["langgraph-supervisor", "create_supervisor"]

        if analysis_result and ("VIRUSTOTAL" in analysis_result or "VirusTotal" in analysis_result):
            tools_used.append("VirusTotal API")

        if analysis_result or threat_result:
            tools_used.append("TavilySearch API")

        if notification_result and ("Email" in notification_result or "enviado" in notification_result.lower()):
            tools_used.append("Mailtrap SMTP")

        # Construir resultado final estructurado
        final_result = {
            "incident_id": incident_id,
            "status": "completed",
            "analysis_result": analysis_result or "No analysis found",
            "threat_assessment": threat_result or "No threat assessment performed",
            "notification_sent": notification_result or "No notification sent",
            "timestamp": datetime.now().isoformat(),
            "tools_used": tools_used,
            "supervisor_architecture": True,
            "apis_real": True,
            "processing_context": processing_context,
            "full_conversation": result.get("messages", [])
        }

        print(f"✅ Procesamiento completado para {incident_id}")
        print(f"🛠️ Tools: {', '.join(tools_used)}")

        return final_result

    except Exception as e:
        print(f"❌ Error en procesamiento SOC: {str(e)}")

        return {
            "incident_id": incident_id,
            "status": "error",
            "error": str(e),
            "timestamp": datetime.now().isoformat(),
            "supervisor_architecture": True,
            "apis_real": True
        }


def _extract_agent_result(workflow_result: dict, agent_name: str) -> str:
    """
    Extrae la salida generada por un agente específico desde el historial del workflow.

    Este método:
    - Recorre todos los mensajes generados durante la ejecución
    - Filtra aquellos relacionados con el agente indicado
    - Devuelve el último mensaje o concatenación de varios

    Args:
        workflow_result (dict): Resultado completo del workflow (incluye historial)
        agent_name (str): Nombre del agente a buscar

    Returns:
        str: Resultado textual del agente (puede ser vacío si no se encuentra)
    """

    try:
        messages = workflow_result.get("messages", [])

        agent_messages = []

        for message in messages:
            # Soporte para objetos tipo LangChain
            if hasattr(message, 'content') and agent_name in str(message).lower():
                agent_messages.append(message.content)

            # Soporte para dicts (modo serializado)
            elif isinstance(message, dict):
                content = message.get('content', '')
                if agent_name in str(message).lower() or agent_name in content.lower():
                    agent_messages.append(content)

        # Devolver último mensaje o concatenación
        if agent_messages:
            return agent_messages[-1] if len(agent_messages) == 1 else "\n\n".join(agent_messages)

        return ""

    except Exception as e:
        print(f"Error extrayendo resultado de {agent_name}: {str(e)}")
        return ""