# Trabalho: Análise de Sincronização Preemptiva e Cooperativa

Este repositório contém os códigos e o relatório do trabalho sobre a implementação e análise comparativa de mecanismos de sincronização.

## Objetivo do Trabalho

O objetivo deste projeto é analisar comparativamente as abordagens de sincronização **preemptiva** e **cooperativa**, utilizando o clássico problema **Produtor-Consumidor** como estudo de caso.

## Implementações

O problema Produtor-Consumidor foi implementado de duas formas distintas para permitir a comparação:

1.  **Sincronização Preemptiva (Threads)**
    * **Linguagem:** C++
    * **Conceito:** Utiliza Threads, onde o Sistema Operacional gerencia a troca de contexto e o escalonamento das tarefas.

2.  **Sincronização Cooperativa (Corrotinas)**
    * **Linguagem:** C
    * **Conceito:** Utiliza Corrotinas, onde as próprias tarefas devem ceder voluntariamente o controle para permitir a execução de outras.
