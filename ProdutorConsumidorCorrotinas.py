import asyncio
import time
import matplotlib.pyplot as plt
import csv

# =============================
# Simulador Produtor-Consumidor
# =============================

async def run_simulation(buffer_size, num_produtores=2, itens_produtor=15, num_consumidores=3):
    fila = asyncio.Queue(maxsize=buffer_size) # fila compartilhada
    buffer_log = []     # tamanho do buffer ao longo do tempo
    tempo_log = []      # timestamp relativo ao início

    inicio = time.time()

    # função produtora
    async def produtora(produtorID):
        for i in range(itens_produtor):
            item = f"item-{produtorID}-{i}"
            await asyncio.sleep(10) # simula tempo de produção (pausa cooperativa)
            await fila.put(item)
            print(f"[Produtor {produtorID}] produziu {item} | Buffer: {fila.qsize()}/{buffer_size}")
        print(f"[Produtor {produtorID}] terminou.")

    # função consumidora
    async def consumidora(consumidorID):
        try:
            while True:
                item = await fila.get()
                print(f"[Consumidor {consumidorID}] pegou {item} | Buffer: {fila.qsize()}/{buffer_size}")
                await asyncio.sleep(20) # simula o tempo de consumo (pausa cooperativa)
                fila.task_done() # sinaliza que o item foi processado
                print(f"[Consumidor {consumidorID}] consumiu {item}")
        except asyncio.CancelledError:
            print(f"Consumidor {consumidorID} encerrado.")
            return
        
    # função que monitora periodicamente o tamanho do buffer
    async def monitora(fila):
        try:
            while True:
                buffer_log.append(fila.qsize())
                tempo_log.append(time.time() - inicio)
                print(f"[MONITOR] Buffer: {fila.qsize()}/{buffer_size}")
                await asyncio.sleep(5) # verifica a cada 5 segundos
        except asyncio.CancelledError:
            print("[MONITOR] Encerrado.")
            raise

    # função principal
    async def main():

        # cria produtores e consumidores
        produtores = [asyncio.create_task(produtora(i)) for i in range(num_produtores)]
        consumidores = [asyncio.create_task(consumidora(i)) for i in range(num_consumidores)]

        # cria um monitor
        monitor = asyncio.create_task(monitora(fila))

        # espera produtores terminarem
        await asyncio.gather(*produtores)

        # espera todos os itens serem processados
        await fila.join()

        # cancela o loop infinito da função consumidora
        for c in consumidores:
            c.cancel()

        # cancela a função monitora
        monitor.cancel()

        print("Todos os itens foram produzidos e consumidos")

        fim = time.time()
        return fim - inicio, tempo_log, buffer_log

    return await main()

# função para salvar as saídas do programa
def salvar_csv(buffer_size, tempo_log, buffer_log):
    filename = f"buffer_{buffer_size}.csv"
    with open(filename, "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["tempo", "buffer"])
        for t, b in zip(tempo_log, buffer_log):
            writer.writerow([t, b])
    print(f"> CSV salvo como: {filename}")


# ==========================
# Execução dos 3 experimentos
# ==========================

resultados = {}

for buffer_size in [5, 50, 100]:
    print(f"\n=== Executando simulação (buffer={buffer_size}) ===")
    tempo_total, tempo_log, buffer_log = asyncio.run(run_simulation(buffer_size))

    salvar_csv(buffer_size, tempo_log, buffer_log)

    resultados[buffer_size] = (tempo_total, tempo_log, buffer_log)
    print(f"Tempo total (buffer={buffer_size}) = {tempo_total:.2f} s")


# ==========================
# Gráfico de comparação
# ==========================

plt.figure(figsize=(12, 6))

for buffer_size, (tempo_total, tempo_log, buffer_log) in resultados.items():
    plt.plot(tempo_log, buffer_log, label=f"Buffer {buffer_size}")

plt.title("Comparação do comportamento do buffer (5 × 50 × 100)")
plt.xlabel("Tempo (s)")
plt.ylabel("Itens no buffer")
plt.legend()
plt.grid(True)
plt.tight_layout()
plt.show()

# Resumo final
print("\nResumo dos tempos totais:")
for b, (tempo_total, _, _) in resultados.items():
    print(f"Buffer {b}: {tempo_total:.2f} s")
