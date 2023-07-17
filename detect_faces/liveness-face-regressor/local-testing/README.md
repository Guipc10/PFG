Autor: Igor Marques

Sobre essa pasta
    A ideia desta pasta é criar uma estrutura de testes para o face-regressor. Os testes são para as coordenadas de ROI, retornadas na requisição. Para comparar os resultados dos testes existe um ground truth em "../../results/ground_truth". Os testes realizados ficam salvos em "../../results/testing", mas eles NÃO são trackeados pelo git. A ideia dos testes é ter um recurso para testar se uma nova rede no face-regressor vai ser consistente ou se dará resultados muito distintos.
    Para fazer um teste:
        1. Criar/ativar um venv com as dependências em requirements.txt
        2. Deixar um servidor rodando localmente:
            python3 face-server.py
        3. Alterar o arquivo test_face_regressor.py conferindo
            * A porta do servidor (por padrão é a 4010)
            * A URL do servidor (localhost)
            * Os caminhos base contendo os arquivos com as imagens (TRUE_PATH e FRAUD_PATH). Esses caminhos devem ter subpastas, e cada subpasta deve ter os arquivos .jpg/.png das imagens
        4. Rodar os testes com:
            python3 test_face_regressor.py
