"""
Utilitário para parsing e formatação de SSID
Suporta múltiplos formatos de entrada
"""
import json
import re
from typing import Dict, Any, Optional, Tuple
from loguru import logger


def parse_ssid(ssid_input: str) -> Optional[Dict[str, Any]]:
    """
    Parse SSID APENAS no formato completo 42["auth",{...}]
    
    Args:
        ssid_input: SSID no formato completo obrigatório
        
    Returns:
        Dict com dados parseados ou None se inválido
    """
    if not ssid_input or not isinstance(ssid_input, str):
        logger.error("❌ SSID deve ser uma string não vazia")
        return None
    
    ssid_input = ssid_input.strip()
    
    # Aceita APENAS formato completo: 42["auth",{...}]
    if not ssid_input.startswith('42["auth"'):
        logger.error("❌ SSID deve estar no formato completo: 42[\"auth\",{...}]")
        logger.info("💡 Use tools/get_ssid.py para obter o formato correto")
        return None
    
    try:
        return _parse_complete_auth_message(ssid_input)
        
    except Exception as e:
        logger.error(f"❌ Erro ao parsear SSID: {e}")
        return None


def _parse_complete_auth_message(ssid_input: str) -> Optional[Dict[str, Any]]:
    """Parse formato completo: 42["auth",{...}]"""
    try:
        # Remove o prefixo 42 e parse como JSON
        json_part = ssid_input[2:]  # Remove "42"
        logger.debug(f"🔍 Tentando parsear: {json_part[:200]}...")
        
        # Tentar corrigir problemas com escape de aspas na session
        if '"session":"a:' in json_part:
            logger.info("🔧 Detectado session PHP serializado - ajustando escape")
            # Escapar aspas internas na session serializada
            import re
            # Encontrar session serializada e escapar aspas internas
            pattern = r'"session":"([^"]*?)"'
            matches = re.findall(pattern, json_part)
            if matches:
                session_content = matches[0]
                # Escapar aspas internas
                escaped_session = session_content.replace('"', '\\"')
                json_part = json_part.replace(f'"session":"{session_content}"', f'"session":"{escaped_session}"')
                logger.debug(f"🔧 JSON corrigido: {json_part[:200]}...")
        
        data = json.loads(json_part)
        
        if isinstance(data, list) and len(data) >= 2 and data[0] == "auth":
            auth_data = data[1]
            if isinstance(auth_data, dict):
                # Verificar se o session é serializado do PHP (conta real)
                if "session" in auth_data and isinstance(auth_data["session"], str):
                    session_data = auth_data["session"]
                    
                    # Se parece ser serializado do PHP (conta real)
                    if session_data.startswith('a:') or 'session_id' in session_data:
                        logger.info("🔍 Detectado session serializado PHP (conta real)")
                        # Aceitar como está - a API vai lidar com isso
                        logger.success("✅ SSID completo de conta real parseado")
                        return auth_data
                    else:
                        # Session normal (demo)
                        logger.info("🎮 Detectado session normal (demo)")
                
                logger.success("✅ SSID completo parseado com sucesso")
                return auth_data
                
        logger.warning("⚠️ Formato de auth message inválido")
        return None
        
    except json.JSONDecodeError as e:
        logger.error(f"❌ Erro JSON no auth message: {e}")
        # Tentar uma abordagem mais simples - extrair manualmente
        logger.info("🔧 Tentando extração manual do JSON...")
        return _extract_auth_data_manually(ssid_input)


def _extract_auth_data_manually(ssid_input: str) -> Optional[Dict[str, Any]]:
    """Extração manual quando JSON parser falha"""
    try:
        import re
        
        # Encontrar a posição da session e extrair até a vírgula seguinte  
        session_start = ssid_input.find('"session":"') + len('"session":"')
        if session_start == -1 + len('"session":"'):
            return None
            
        # Encontrar onde termina a session (antes de ","isDemo")
        session_end = ssid_input.find('","isDemo"', session_start)
        if session_end == -1:
            session_end = ssid_input.find('", "isDemo"', session_start)
        if session_end == -1:
            return None
            
        session_value = ssid_input[session_start:session_end]
        
        # Extrair outros campos com regex simples
        demo_match = re.search(r'"isDemo":(\d+)', ssid_input)
        uid_match = re.search(r'"uid":(\d+)', ssid_input)
        platform_match = re.search(r'"platform":(\d+)', ssid_input)
        fast_history_match = re.search(r'"isFastHistory":(true|false)', ssid_input)
        optimized_match = re.search(r'"isOptimized":(true|false)', ssid_input)
        
        auth_data = {
            "session": session_value,
            "isDemo": int(demo_match.group(1)) if demo_match else 1,
            "uid": int(uid_match.group(1)) if uid_match else 0,
            "platform": int(platform_match.group(1)) if platform_match else 2,
        }
        
        if fast_history_match:
            auth_data["isFastHistory"] = fast_history_match.group(1) == "true"
        if optimized_match:
            auth_data["isOptimized"] = optimized_match.group(1) == "true"
        
        logger.success("✅ SSID extraído manualmente com sucesso")
        logger.info(f"🔍 Session completa: {len(session_value)} caracteres")
        logger.debug(f"🔍 Session (início): {session_value[:50]}...")
        logger.debug(f"🔍 Session (fim): ...{session_value[-50:]}")
        return auth_data
            
    except Exception as e:
        logger.error(f"❌ Erro na extração manual: {e}")
    
    return None


def _parse_json_object(ssid_input: str) -> Optional[Dict[str, Any]]:
    """Parse formato JSON: {...}"""
    try:
        auth_data = json.loads(ssid_input)
        if isinstance(auth_data, dict) and "session" in auth_data:
            logger.success("✅ JSON SSID parseado com sucesso")
            return auth_data
        else:
            logger.warning("⚠️ JSON não contém campo 'session'")
            return None
            
    except json.JSONDecodeError as e:
        logger.error(f"❌ Erro JSON: {e}")
        return None


def _is_session_id_format(ssid_input: str) -> bool:
    """Verifica se é um session ID puro"""
    # Session IDs são tipicamente strings alfanuméricas de 20-50 caracteres
    return (
        len(ssid_input) >= 10 and 
        len(ssid_input) <= 100 and
        re.match(r'^[a-zA-Z0-9_-]+$', ssid_input)
    )


def _create_default_auth_data(session_id: str) -> Dict[str, Any]:
    """Cria dados de auth padrão para session ID puro"""
    logger.info("🔧 Criando dados de auth padrão para session ID")
    return {
        "session": session_id,
        "isDemo": 1,  # Padrão demo
        "uid": 0,     # UID desconhecido
        "platform": 1,  # Web platform
        "isFastHistory": True
    }


def _extract_json_from_string(ssid_input: str) -> Optional[Dict[str, Any]]:
    """Tenta extrair JSON de strings complexas"""
    try:
        # Procura por padrões JSON na string
        json_patterns = [
            r'\{[^}]*"session"[^}]*\}',  # JSON com session
            r'\{.*?\}',  # Qualquer JSON
        ]
        
        for pattern in json_patterns:
            matches = re.findall(pattern, ssid_input)
            for match in matches:
                try:
                    data = json.loads(match)
                    if isinstance(data, dict) and "session" in data:
                        logger.success("✅ JSON extraído de string complexa")
                        return data
                except:
                    continue
                    
        return None
        
    except Exception:
        return None


def format_session_id(
    session_id: str,
    is_demo: bool = True,
    uid: int = 0,
    platform: int = 1,
    is_fast_history: bool = True,
) -> str:
    """
    Format session ID for authentication

    Args:
        session_id: Raw session ID
        is_demo: Whether this is a demo account
        uid: User ID
        platform: Platform identifier (1=web, 3=mobile)
        is_fast_history: Enable fast history loading

    Returns:
        str: Formatted session message
    """
    auth_data = {
        "session": session_id,
        "isDemo": 1 if is_demo else 0,
        "uid": uid,
        "platform": platform,
    }

    if is_fast_history:
        auth_data["isFastHistory"] = True

    return f'42["auth",{json.dumps(auth_data)}]'


def process_ssid_input(
    ssid_input: str, 
    force_demo: Optional[bool] = None,
    force_uid: Optional[int] = None
) -> Tuple[Optional[str], Optional[Dict[str, Any]]]:
    """
    Processa SSID no formato completo obrigatório
    
    Args:
        ssid_input: SSID no formato completo 42["auth",{...}]
        force_demo: Forçar modo demo (sobrescreve valor do SSID)
        force_uid: Forçar UID específico
        
    Returns:
        Tuple[formatted_ssid, parsed_data]
    """
    # Parse do input - apenas formato completo
    parsed = parse_ssid(ssid_input)
    
    if not parsed:
        logger.error("❌ SSID deve estar no formato: 42[\"auth\",{\"session\":\"...\",\"isDemo\":1,...}]")
        return None, None
    
    # Aplicar overrides se fornecidos
    if force_demo is not None:
        parsed["isDemo"] = 1 if force_demo else 0
        logger.info(f"🔧 Modo demo forçado: {force_demo}")
    
    if force_uid is not None:
        parsed["uid"] = force_uid
        logger.info(f"🔧 UID forçado: {force_uid}")
    
    # Garantir campos obrigatórios
    parsed.setdefault("platform", 1)
    parsed.setdefault("isFastHistory", True)
    
    # Formatar SSID final
    formatted_ssid = format_session_id(
        session_id=parsed["session"],
        is_demo=bool(parsed.get("isDemo", 1)),
        uid=parsed.get("uid", 0),
        platform=parsed.get("platform", 1),
        is_fast_history=parsed.get("isFastHistory", True)
    )
    
    logger.success("✅ SSID formato completo validado com sucesso")
    logger.debug(f"📋 Dados extraídos: {parsed}")
    
    return formatted_ssid, parsed


def validate_ssid_format(ssid: str) -> bool:
    """
    Valida se SSID está no formato correto
    
    Args:
        ssid: SSID para validar
        
    Returns:
        bool: True se válido
    """
    try:
        if not ssid.startswith('42["auth"'):
            return False
            
        # Parse para verificar estrutura
        parsed = parse_ssid(ssid)
        
        if not parsed:
            return False
            
        # Verificar campos obrigatórios
        required_fields = ["session"]
        for field in required_fields:
            if field not in parsed:
                return False
                
        # Verificar tipos
        if not isinstance(parsed["session"], str) or len(parsed["session"]) < 5:
            return False
            
        return True
        
    except Exception:
        return False


# Função de conveniência para uso direto
def auto_format_ssid(ssid_input: str, demo: bool = True) -> Optional[str]:
    """
    Valida SSID no formato completo obrigatório
    
    Args:
        ssid_input: SSID no formato completo 42["auth",{...}]
        demo: Forçar modo demo
        
    Returns:
        str: SSID validado ou None se inválido
    """
    # Apenas valida - não formata automaticamente
    parsed = parse_ssid(ssid_input)
    if not parsed:
        return None
    
    # Aplica override de demo se necessário
    if demo != bool(parsed.get("isDemo", 1)):
        logger.info(f"🔧 Ajustando modo demo para: {demo}")
        formatted_ssid = format_session_id(
            session_id=parsed["session"],
            is_demo=demo,
            uid=parsed.get("uid", 0),
            platform=parsed.get("platform", 1),
            is_fast_history=parsed.get("isFastHistory", True)
        )
        return formatted_ssid
    
    # Se já está no formato correto, retorna como está
    return ssid_input
