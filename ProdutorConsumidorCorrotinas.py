import asyncio
import time

inicio = time.time()

# fila compartilhada
fila = asyncio.Queue()

# função produtora
async def produtora(produtorID, numItems):
    for i in range(numItems):
        item = f"item-{produtorID}-{i}"
        await asyncio.sleep(10)  # simula tempo de produção (pausa cooperativa)
        await fila.put(item)
        print("Produtor", produtorID, "produzio o", item, "| Buffer atual:", {fila.qsize()})

# função consumidora
async def consumidora(consumidorID):
    while True:
        item = await fila.get()
        print("Consumidor", consumidorID, "pegou o", item, "| Buffer atual:", {fila.qsize()})
        await asyncio.sleep(20)  # simula tempo de consumo (pausa cooperativa)
        fila.task_done()  # sinaliza que o item foi processado
        print("Consumidor", consumidorID, "consumiu o", item)

# funçaõ que monitora periodicamente o tamanho do buffer
async def monitora(fila):
    while True:
        print("Buffer atual:", {fila.qsize()}, "itens" )
        await asyncio.sleep(10)  # verifica a cada 10 segundos

# função principal
async def main():
    # cria produtores e consumidores
    produtores = [asyncio.create_task(produtora(i, 5)) for i in range(2)]
    consumidores = [asyncio.create_task(consumidora(i)) for i in range(3)]
    
    # cria um monitor
    monitor = asyncio.create_task(monitora(fila))

    # espera produtores terminarem
    await asyncio.gather(*produtores)

    # espera todos os itens serem processados
    await fila.join()

    # cancela o loop infinito da função consumidora
    for c in consumidores:
        c.cancel()
    
    print("Todos os itens foram produzidos e consumidos")

asyncio.run(main())

fim = time.time()

tempo = fim - inicio
print("Tempo total:", tempo, "segundos")