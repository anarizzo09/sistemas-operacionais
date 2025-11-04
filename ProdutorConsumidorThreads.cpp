#include <iostream>
#include <thread>
#include <mutex>
#include <condition_variable>
#include <chrono>
#include <vector>

using namespace std;

class Semaphore {
public:
    Semaphore(int initial_count = 0) : count_(initial_count) {}

    void wait() {
        unique_lock<mutex> lock(mutex_);
        cv_.wait(lock, [this] { return count_ > 0; });
        count_--;
    }

    // Equivale a sem.signal() (incrementa a contagem, notifica uma thread)
    void signal() {
        unique_lock<mutex> lock(mutex_);
        count_++;
        cv_.notify_one();
    }

private:
    mutex mutex_;
    condition_variable cv_;
    int count_;
};

// --- VARIÁVEIS GLOBAIS (Buffer e Semáforos) ---
const int BUFFER_SIZE = 5;
vector<int> buffer;
int item_counter = 0; // Contador global de itens produzidos.

// 1. Mutex (Exclusão Mútua, valor inicial 1)
mutex buffer_mutex; 

// 2. Items (Conta itens, valor inicial 0)
Semaphore items(0); 

// 3. Spaces (Conta espaços vazios, valor inicial BUFFER_SIZE)
Semaphore spaces(BUFFER_SIZE); 

const int MAX_ITERACOES = 50;

// --- FUNÇÃO PRODUTORA ---
void produtora() {
    cout << "Iniciando Produtora...\n";
    
    for (int i = 0; i < MAX_ITERACOES; ++i) {
        
        // Simula waitForEvent() (I/O BOUND)
        this_thread::sleep_for(chrono::milliseconds(10));
        int produced_item = ++item_counter;

        // 1. Espera por Espaço (spaces.wait())
        spaces.wait(); 

        // 2. Adquire o Mutex (mutex.wait())
        unique_lock<mutex> lock(buffer_mutex);

        // --- REGIÃO CRÍTICA (buffer.add(event)) ---
        buffer.push_back(produced_item);
        // cout << "-> Produziu: " << produced_item << ". Buffer size: " << buffer.size() << endl;
        // --- FIM REGIÃO CRÍTICA ---

        // 3. Libera o Mutex (mutex.signal())
        // O unique_lock faz isso automaticamente.

        // 4. Sinaliza Item (items.signal())
        items.signal(); 
    }
}

// --- FUNÇÃO CONSUMIDORA ---
void consumidora() {
    cout << "Iniciando Consumidora...\n";

    for (int i = 0; i < MAX_ITERACOES; ++i) {
        
        // 1. Espera por Item (items.wait())
        items.wait();

        // 2. Adquire o Mutex (mutex.wait())
        unique_lock<mutex> lock(buffer_mutex);

        // --- REGIÃO CRÍTICA (event = buffer.get()) ---
        int consumed_item = buffer.front();
        buffer.erase(buffer.begin());
        // cout << "<- Consumiu: " << consumed_item << ". Buffer size: " << buffer.size() << endl;
        // --- FIM REGIÃO CRÍTICA ---

        // 3. Libera o Mutex (mutex.signal())
        // O unique_lock faz isso automaticamente.

        // 4. Sinaliza Espaço (spaces.signal())
        spaces.signal();

        // 5. Simula event.process() (CPU BOUND)
        this_thread::sleep_for(chrono::milliseconds(20));
    }
}

// --- FUNÇÃO PRINCIPAL ---
int main() {
    
    auto start = chrono::high_resolution_clock::now();

    thread prod(produtora);
    thread cons(consumidora);
    
    prod.join();
    cons.join();

    auto end = chrono::high_resolution_clock::now();
    chrono::duration<double, milli> duration = end - start;

    cout << "\n--- Execução Concluída (Modelo Semáforo) ---\n";
    cout << "Itens esperados: " << MAX_ITERACOES << ", Itens produzidos: " << item_counter << ".\n";
    cout << "Buffer final size: " << buffer.size() << " (deve ser 0).\n";
    cout << "Tempo total de execução (ms): " << duration.count() << "\n";
    
    return 0;
}