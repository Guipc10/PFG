
Antes de executar os scripts, caso esteja em uma máquina que não seja a dev é preciso exportar as variáveis de ambiente que apontam pra dev:
    
    source src/urls_and_paths.sh

Para gerar ground truths, em src/:
    
    1) Rodar
        python3 gen_ground_truths.py
            -> baixa os dados
            -> cria os ground truths
    
Para executar os testes (com docker):
    
    1) Rodar
        ./build_and_run.sh
            -> constrói a imagem
            -> executa o serviço de teste
        
Para executar os testes (com docker) em máquina sem permissões especiais, usando um arquivo .env com as variáveis de acesso da AWS:
    
    1) Alterar no build_and_run_with_envfile.sh o caminho para esse arquivo (flag --env-file)
    2) Rodar:
        ./build_and_run_with_envfile.sh
            -> constrói a imagem
            -> executa o serviço de teste
        
       
