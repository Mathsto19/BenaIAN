# BenIAN – Emulador de Calculadora Gráfica para Desktop

Aplicação desktop focada em UI/UX e visualização matemática, desenvolvida como um projeto prático para explorar interfaces interativas e simular funcionalidades de calculadoras gráficas científicas.

![Python](https://img.shields.io/badge/Python-3776AB?style=flat-square&logo=python&logoColor=white)
![Tkinter](https://img.shields.io/badge/Tkinter-FFD43B?style=flat-square&logo=python&logoColor=blue)

---

## Sobre o Projeto

O BenIAN é um simulador de calculadora gráfica inspirado em dispositivos como a HP Prime, projetado para oferecer uma experiência interativa de visualização matemática diretamente no computador. O projeto explora conceitos de UI/UX responsiva e renderização de funções matemáticas em tempo real.

---

## Funcionalidades

### Implementado
- Renderização de funções matemáticas
- Interface interativa e responsiva
- Operações científicas e avançadas
- Tela inicial com Guard
- Entrada de expressões matemáticas

### Em desenvolvimento

#### Botões não implementados
| Botão | Atalho | Função planejada |
|-------|--------|------------------|
| Mem | Shift + Mem | Gerenciador de memória |
| Units | Shift + Units | Menu de conversão de unidades |
| List | Shift + 7 | Editor e operações de lista |
| Matrix | Shift + 8 | Editor e operações de matriz |
| Settings | Shift + Home | Configurações da calculadora |
| Info | Shift + Apps | Informações do sistema |
| User | Shift + Help | Variáveis do usuário |

#### Botões silenciosos (sem feedback visual)
| Botão | Função esperada |
|-------|-----------------|
| View | Mudar visualização (plot vs. tabela) |
| Menu | Menu contextual inferior |
| Help | Ajuda contextual |
| Def (Shift + x) | Definir função rapidamente |
| Note (Shift + 0) | Editor de notas de texto |
| Base (Shift + -) | Conversão de base (Hex/Bin/Oct) |
| Setup | Configuração específica da App atual |

#### Botões com comportamento incorreto
| Botão | Comportamento atual | Comportamento esperado |
|-------|----------------------|------------------------|
| Vars | Não implementado | Abrir menu de variáveis (A–Z, Home, App) |
| Logic (Shift + 9) | Não implementado | Abrir operadores lógicos (AND, OR, XOR) |
| Prog (Shift + 1) | Não implementado | Abrir catálogo de programas |
| Eval (Shift + ,) | Digita "Eval" | Forçar avaliação numérica/simbólica |

---

## Tecnologias

- Python 3.10+
- Tkinter – Interface gráfica nativa
- math e NumPy – Cálculos matemáticos (conforme o módulo utilizado no projeto)

---

## Como usar

### Instalação
```bash
# Clone o repositório
git clone https://github.com/Mathsto19/BenIAN.git
cd BenIAN

# Execute o aplicativo
python BenIAN.py
````

### Controles básicos

* Entrada de funções: digite expressões matemáticas na área de entrada
* Plotar gráficos: insira funções e visualize em tempo real
* Operações científicas: use os botões para funções trigonométricas, logarítmicas, etc.

---

## Roadmap

* [ ] Implementar gerenciador de memória (Mem)
* [ ] Adicionar conversão de unidades (Units)
* [ ] Criar editor de listas (List) e matrizes (Matrix)
* [ ] Implementar menu de configurações (Settings)
* [ ] Corrigir comportamento dos botões Vars, Logic, Prog, Eval
* [ ] Adicionar feedback visual para botões silenciosos
* [ ] Melhorar tela inicial com Guard

---

## Inspiração

O BenIAN se inspira no conceito de calculadoras gráficas científicas, que oferecem recursos de plotagem de equações, operações avançadas e ferramentas de apoio à visualização matemática.

---

## Suporte e contato

Para dúvidas ou colaborações:

* Matheus Augusto — [matheusaugustooliveira@alunos.utfpr.edu.br](mailto:matheusaugustooliveira@alunos.utfpr.edu.br)

---

## Licença

Distribuição autorizada apenas para fins acadêmicos, científicos e de pesquisa. Uso comercial ou redistribuição sem permissão é proibido.
