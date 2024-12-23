import sys
import os
from InquirerPy import inquirer
from InquirerPy.base import Choice
from cryptography.fernet import InvalidToken
from types import SimpleNamespace
from model.password import Password
from views.password_views import FernetHasher

# Adiciona o diretório atual ao path
sys.path.append(os.path.abspath(os.curdir))

def criar_nova_senha():
    try:
        if len(Password.get()) == 0: # Verificar se é o primeiro uso if true: cria o Passwoed.txt
            key, path = FernetHasher.create_key(archive=True)
            print('🔑 Sua chave foi criada com sucesso. SALVE-A COM CUIDADO!')
            print(f'Chave: {key.decode("utf-8")}')
            if path:
                print('⚠️ Chave salva no arquivo.')
                print(f'📍 Caminho: {path}')
                print('Lembre-se de remover o arquivo após transferir de local.')
        validate_data = validate_not_empty('A chave')
        key = inquirer.text(
            message="Digite a chave usada para criptografia:",
            validate=validate_data.validate,
            invalid_message=validate_data.invalid_message,
            qmark=''
        ).execute()
        try:
            fernet_user = FernetHasher(key)
        except Exception as e:
            print(f"❌ Erro ao salvar senha: {e}")
            return
        validate_data = validate_not_empty('O domínio')
        domain = inquirer.text(
            message="Domínio (ex: gmail, banco):",
            validate=validate_data.validate,
            invalid_message=validate_data.invalid_message,
            qmark='').execute()
        validate_data=validate_not_empty('A senha')
        password = inquirer.secret(
            message="Senha:",
            validate=validate_data.validate,
            invalid_message=validate_data.invalid_message,
            qmark=''
        ).execute()
        inquirer.secret(
            message="Digite novamente a senha:",
            validate=lambda text: text == password, 
            invalid_message="❌ As senhas não coincidem. Tente novamente.",
            qmark=''
        ).execute()
        password = password.strip()
        encrypted_password = fernet_user.encrypt(password).decode('utf-8')
        p1 = Password(domain=domain, password=encrypted_password)
        p1.save()
        print('✅ Senha salva com sucesso!')
    except Exception as e:
        print(f"❌ Erro inesperado: {e}")

def recuperar_senha():
    try:
        while True:
            validate_data=validate_not_empty('O Domínio')
            domain = inquirer.text(
                message="Domínio para buscar a senha:",
                validate=validate_data.validate,
                invalid_message=validate_data.invalid_message,
                qmark=''
            ).execute()
            data = Password.get()
            matching_domains = [
                i['domain'] for i in data 
                if domain.lower() in i['domain'].lower()
            ]
            if not matching_domains:
                print('🔍 Domímio não encontrado.')
                continue
            break
        while True:
            validate_data = validate_not_empty('A chave')
            key = inquirer.text(
            message="Digite a chave de descriptografia:",
            validate=validate_data.validate,
            invalid_message=validate_data.invalid_message,
            qmark=''
            ).execute()
            try:
                fernet_user: FernetHasher = FernetHasher(key)
                data = Password.get()
                passwords = [
                    fernet_user.decrypt(i['password']) 
                    for i in data 
                    if domain.lower() in i['domain'].lower()
                ]
                if passwords:
                    print('🔓 Senhas encontradas:')
                    for idx, pwd in enumerate(passwords, 1):
                        print(f"{idx}. {pwd}")
                else:   
                    print('🔍 Nenhuma senha encontrada para este domínio.')
            except InvalidToken:
                print("❌ Chave inválida! Verifique a chave de descriptografia.")
                continue
            except Exception as e:
                print(f"❌ Erro ao recuperar senha: {e}")
                continue
            break
    except Exception as e:
        print(f"❌ Erro inesperado: {e}")
        
def validate_not_empty(complemento_msg: str) -> SimpleNamespace:
    return SimpleNamespace(
        validate = lambda x: isinstance(x, str) and len(x.strip()) > 0 ,
        invalid_message = f"❌ {complemento_msg} não pode estar vazio!"
    )
    
def main():
    while True:
        try:
            action = inquirer.select(
                message="🔐 Gerenciador de Senhas",
                choices=[
                    Choice(value='1', name='1. Salvar nova senha'),
                    Choice(value='2', name='2. Recuperar senha'),
                    Choice(value='0', name='0. Sair')
                ],
                qmark='', border=True, max_height=3
            ).execute()
            if action == '1': criar_nova_senha()
            elif action == '2': recuperar_senha()
            elif action == '0':
                print("👋 Saindo...")
                break
            else:
                print("❌ Opção inválida! Tente novamente.")
        except KeyboardInterrupt:
            print("\n👋 Saindo...")
            break
        except Exception as e:
            print(f"❌ Erro inesperado: {e}")
            