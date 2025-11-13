"""
Testes unitários para o parser de SSID
Autor: AdminhuDev
"""

import unittest
import sys
import os

# Adicionar o diretório raiz ao path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from pocketoptionapi.ssid_parser import (
    parse_ssid,
    validate_ssid_format,
    process_ssid_input,
    format_session_id,
    auto_format_ssid
)


class TestSSIDParser(unittest.TestCase):
    """
    Testes para o parser de SSID
    """

    def setUp(self):
        """Configuração inicial para cada teste"""
        # SSIDs de teste válidos
        self.valid_complete_ssid = '42["auth",{"session":"test_session_123","isDemo":1,"uid":123456,"platform":2}]'
        self.valid_json_ssid = '{"session":"test_session_123","isDemo":1,"uid":123456,"platform":2}'
        self.valid_session_only = 'test_session_123'

        # SSIDs inválidos para teste
        self.invalid_ssid = "invalid_format"
        self.empty_ssid = ""

    def test_parse_ssid_valid_complete(self):
        """Teste de parsing de SSID completo válido"""
        result = parse_ssid(self.valid_complete_ssid)

        self.assertIsNotNone(result)
        self.assertIsInstance(result, dict)
        self.assertIn("session", result)
        self.assertIn("isDemo", result)
        self.assertIn("uid", result)
        self.assertIn("platform", result)
        self.assertEqual(result["session"], "test_session_123")
        self.assertEqual(result["isDemo"], 1)
        self.assertEqual(result["uid"], 123456)
        self.assertEqual(result["platform"], 2)

    def test_parse_ssid_invalid_format(self):
        """Teste de parsing de SSID com formato inválido"""
        result = parse_ssid(self.invalid_ssid)
        self.assertIsNone(result)

    def test_parse_ssid_empty(self):
        """Teste de parsing de SSID vazio"""
        result = parse_ssid(self.empty_ssid)
        self.assertIsNone(result)

    def test_parse_ssid_none(self):
        """Teste de parsing de SSID None"""
        result = parse_ssid(None)
        self.assertIsNone(result)

    def test_validate_ssid_format_valid(self):
        """Teste de validação de SSID válido"""
        result = validate_ssid_format(self.valid_complete_ssid)
        self.assertTrue(result)

    def test_validate_ssid_format_invalid(self):
        """Teste de validação de SSID inválido"""
        result = validate_ssid_format(self.invalid_ssid)
        self.assertFalse(result)

    def test_validate_ssid_format_empty(self):
        """Teste de validação de SSID vazio"""
        result = validate_ssid_format(self.empty_ssid)
        self.assertFalse(result)

    def test_format_session_id(self):
        """Teste de formatação de session ID"""
        session_id = "test_session_123"
        result = format_session_id(
            session_id=session_id,
            is_demo=True,
            uid=123456,
            platform=2
        )

        expected = '42["auth",{"session":"test_session_123","isDemo":1,"uid":123456,"platform":2}]'
        self.assertEqual(result, expected)

    def test_format_session_id_with_fast_history(self):
        """Teste de formatação com fast history habilitado"""
        session_id = "test_session_123"
        result = format_session_id(
            session_id=session_id,
            is_demo=False,
            uid=123456,
            platform=2,
            is_fast_history=True
        )

        self.assertIn('"isFastHistory":true', result)
        self.assertIn('"isDemo":0', result)

    def test_process_ssid_input_valid(self):
        """Teste de processamento de SSID válido"""
        formatted_ssid, parsed_data = process_ssid_input(self.valid_complete_ssid)

        self.assertIsNotNone(formatted_ssid)
        self.assertIsNotNone(parsed_data)
        self.assertEqual(formatted_ssid, self.valid_complete_ssid)
        self.assertIsInstance(parsed_data, dict)

    def test_process_ssid_input_invalid(self):
        """Teste de processamento de SSID inválido"""
        formatted_ssid, parsed_data = process_ssid_input(self.invalid_ssid)

        self.assertIsNone(formatted_ssid)
        self.assertIsNone(parsed_data)

    def test_process_ssid_input_with_force_demo(self):
        """Teste de processamento com override de demo"""
        # SSID com isDemo=0
        ssid_with_real = '42["auth",{"session":"test_session_123","isDemo":0,"uid":123456,"platform":2}]'

        formatted_ssid, parsed_data = process_ssid_input(ssid_with_real, force_demo=True)

        self.assertIsNotNone(formatted_ssid)
        self.assertIsNotNone(parsed_data)
        # Deve ter sido alterado para demo
        self.assertIn('"isDemo":1', formatted_ssid)

    def test_process_ssid_input_with_force_uid(self):
        """Teste de processamento com override de UID"""
        formatted_ssid, parsed_data = process_ssid_input(
            self.valid_complete_ssid,
            force_uid=999999
        )

        self.assertIsNotNone(formatted_ssid)
        self.assertIsNotNone(parsed_data)
        # Deve ter sido alterado para o UID forçado
        self.assertIn('"uid":999999', formatted_ssid)

    def test_auto_format_ssid_valid(self):
        """Teste de formatação automática de SSID válido"""
        result = auto_format_ssid(self.valid_complete_ssid)
        self.assertEqual(result, self.valid_complete_ssid)

    def test_auto_format_ssid_invalid(self):
        """Teste de formatação automática de SSID inválido"""
        result = auto_format_ssid(self.invalid_ssid)
        self.assertIsNone(result)

    def test_auto_format_ssid_demo_override(self):
        """Teste de formatação automática com override de demo"""
        # SSID com isDemo=0 (conta real)
        ssid_real = '42["auth",{"session":"test_session_123","isDemo":0,"uid":123456,"platform":2}]'

        # Forçar para demo
        result = auto_format_ssid(ssid_real, demo=True)

        self.assertIsNotNone(result)
        self.assertIn('"isDemo":1', result)

    def test_complex_session_parsing(self):
        """Teste de parsing de session complexa (PHP serialized)"""
        # Simular session serializada do PHP
        complex_ssid = '42["auth",{"session":"a:2:{s:10:\\"session_id\\";s:26:\\"complex_session_123\\";s:4:\\"user\\";i:123456;}","isDemo":0,"uid":123456,"platform":2}]'

        result = parse_ssid(complex_ssid)

        self.assertIsNotNone(result)
        self.assertIn("session", result)
        self.assertEqual(result["isDemo"], 0)
        self.assertEqual(result["uid"], 123456)

    def test_session_with_escapes(self):
        """Teste de parsing de session com caracteres de escape"""
        # Session com aspas que precisam ser escapadas
        ssid_with_quotes = '42["auth",{"session":"session_with_\\"quotes\\"","isDemo":1,"uid":123456,"platform":2}]'

        result = parse_ssid(ssid_with_quotes)

        self.assertIsNotNone(result)
        self.assertIn("session", result)
        self.assertEqual(result["session"], 'session_with_"quotes"')

    def test_malformed_json_recovery(self):
        """Teste de recuperação de JSON mal formado"""
        # JSON com problema de formatação
        malformed_json = '42["auth",{"session":"test_session","isDemo":1,"uid":123456,"platform":2'  # Faltando fechamento

        result = parse_ssid(malformed_json)
        # Deve falhar graciosamente
        self.assertIsNone(result)


class TestSSIDEEdgeCases(unittest.TestCase):
    """
    Testes de casos extremos para o parser de SSID
    """

    def test_extremely_long_session(self):
        """Teste com session extremamente longa"""
        long_session = "a" * 1000  # 1000 caracteres
        ssid = f'42["auth",{"session":"{long_session}","isDemo":1,"uid":123456,"platform":2}]'

        result = parse_ssid(ssid)

        self.assertIsNotNone(result)
        self.assertEqual(len(result["session"]), 1000)

    def test_unicode_session(self):
        """Teste com session contendo caracteres unicode"""
        unicode_session = "test_ñáéíóú_中文_русский"
        ssid = f'42["auth",{"session":"{unicode_session}","isDemo":1,"uid":123456,"platform":2}]'

        result = parse_ssid(ssid)

        self.assertIsNotNone(result)
        self.assertEqual(result["session"], unicode_session)

    def test_minimum_valid_ssid(self):
        """Teste com SSID mínimo válido"""
        min_ssid = '42["auth",{"session":"a","isDemo":0,"uid":1,"platform":1}]'

        result = parse_ssid(min_ssid)

        self.assertIsNotNone(result)
        self.assertEqual(result["session"], "a")
        self.assertEqual(result["isDemo"], 0)
        self.assertEqual(result["uid"], 1)
        self.assertEqual(result["platform"], 1)

    def test_missing_optional_fields(self):
        """Teste com campos opcionais faltando"""
        ssid_no_platform = '42["auth",{"session":"test_session","isDemo":1,"uid":123456}]'

        result = parse_ssid(ssid_no_platform)

        self.assertIsNotNone(result)
        self.assertEqual(result["session"], "test_session")
        self.assertEqual(result["isDemo"], 1)
        self.assertEqual(result["uid"], 123456)
        # Deve ter valor padrão para platform
        self.assertEqual(result.get("platform", 1), 1)


if __name__ == '__main__':
    # Executar testes
    unittest.main(verbosity=2)
