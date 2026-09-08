# -*- coding: utf-8 -*-
import os
import subprocess
import sys
from datetime import datetime

# Garante que a execução ocorra no diretório raiz do projeto
PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))
os.chdir(PROJECT_ROOT)

BASE_BRANCH = "main"

def run_command(command, allow_fail=False):
    print("\n[RUN] " + command)
    return_code = subprocess.call(command, shell=True)
    if return_code != 0 and not allow_fail:
        print("❌ Erro na execução do comando: " + command)
        sys.exit(return_code)
    return return_code

def preflight_check():
    """Valida todo o ambiente antes de tocar no Git ou instalar dependências."""
    print("🔍 [TESTE PRÉVIO] Validando o ambiente de execução...")

    # 1. Valida versão do Python
    if sys.version_info[0] < 3:
        print("❌ ERRO: O script requer Python 3. Executável atual: " + sys.executable)
        sys.exit(1)
    print("  ✓ Python 3 verificado: " + sys.version.split()[0])

    # 2. Valida arquivos obrigatórios na pasta
    required_files = ["requirements.txt", "main.py", "src/config.py"]
    missing = [f for f in required_files if not os.path.exists(os.path.join(PROJECT_ROOT, f))]
    if missing:
        print("❌ ERRO: Arquivos ausentes na raiz do projeto: " + ", ".join(missing))
        sys.exit(1)
    print("  ✓ Arquivos estruturais encontrados (" + ", ".join(required_files) + ")")

    # 3. Valida se o diretório é um repositório Git
    git_check = subprocess.call("git rev-parse --is-inside-work-tree", shell=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    if git_check != 0:
        print("❌ ERRO: A pasta não é um repositório Git ou o Git não está instalado.")
        sys.exit(1)
    print("  ✓ Repositório Git detectado")

    # 4. Valida se o workspace Git está limpo para evitar erros no checkout
    try:
        status = subprocess.check_output("git status --porcelain", shell=True).decode("utf-8").strip()
        if status:
            print("⚠️ AVISO: Existem arquivos alterados ou não salvos no Git. Faça commit/stash para permitir a troca de branch.")
            print(status)
            sys.exit(1)
    except Exception as e:
        print("❌ ERRO ao consultar status do Git: " + str(e))
        sys.exit(1)

    print("  ✓ Workspace Git limpo para checkout de branch")
    print("✅ Todos os testes prévios passaram com sucesso!\n")

def main():
    # Executa a verificação antes de qualquer comando pesado
    preflight_check()

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    new_branch = "feature/auto_execution_" + timestamp

    print("Alternando para a branch '" + BASE_BRANCH + "' e criando '" + new_branch + "'...")

    run_command("git checkout " + BASE_BRANCH)
    run_command("git pull origin " + BASE_BRANCH, allow_fail=True) # Permite seguir caso o remoto não esteja configurado ainda
    run_command("git checkout -b " + new_branch)

    print("Branch '" + new_branch + "' criada com sucesso!")

    # Usa o executável Python ativo no ambiente para garantir compatibilidade
    python_exec = sys.executable
    run_command(python_exec + " -m pip install -q -r requirements.txt")
    run_command("playwright install chromium")
    run_command("pytest")
    run_command(python_exec + " main.py --scrape")

    print("\n🎉 Pipeline executado do início ao fim com sucesso na branch '" + new_branch + "'!")

if __name__ == "__main__":
    main()