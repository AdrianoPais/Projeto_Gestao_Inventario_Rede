# Projeto de Gestão de Inventário de Rede

## Link para o site: https://projetogestaoinventariorede.streamlit.app/

Este projeto é uma aplicação robusta desenvolvida em Python para a gestão centralizada de ativos de rede. Permite o registo, monitorização de tráfego e gestão de conectividade de diversos tipos de dispositivos através de uma interface moderna construída com Streamlit.
## Funcionalidades Principais

- Gestão de Dispositivos (CRUD): Adição, listagem e remoção de Routers, Switches, Access Points e Endpoints.

- Controlo de Integridade: Validação rigorosa de endereços IPv4, IPv6 e endereços MAC, garantindo que não existem duplicados no inventário.

- Monitorização de Tráfego: Atualização e acompanhamento do consumo de dados (Upload/Download) para cada utilizador.

- Políticas de Rede: Aplicação de limites de tráfego com suspensão automática de dispositivos que excedam os parâmetros definidos.

- Gestão de Ligações: Mapeamento de ligações físicas entre dispositivos e infraestrutura (Routers/Switches).

- Persistência de Dados: Gravação e leitura de todo o inventário em formato JSON para garantir a continuidade dos dados entre sessões.

## Arquitetura do Projeto

O sistema foi desenhado seguindo os princípios da Programação Orientada a Objetos (POO):

- devices.py: Define a hierarquia de classes dos equipamentos, utilizando herança a partir de uma classe base Device.

- inventory.py: Motor do sistema que gere a coleção de objetos e aplica as regras de negócio e validações globais.

- app_web.py: Interface gráfica (GUI) baseada na web para uma interação intuitiva.

- storage.py: Módulo responsável pela serialização e desserialização de objetos para ficheiros.

- utils.py: Biblioteca de funções auxiliares para validações técnicas (Regex e IPAddress).

## Como Executar Localmente

  Clonar o repositório:
  Bash

    git clone https://github.com/AdrianoPais/Projeto_Gestao_Inventario_Rede.git
    cd Projeto_Gestao_Inventario_Rede

  Instalar as dependências:
  Bash

    pip install streamlit

  Correr a aplicação:
  Bash

    streamlit run app_web.py

## Deploy

A aplicação está configurada para deploy imediato no Streamlit Community Cloud, utilizando o ficheiro requirements.txt para a gestão automática de dependências.

### Autores: Daniel Santos, Sérgio Correia e Tiago Costa. Curso: GRSC0925 - UC00608 Programação Alocada a Objetos.
