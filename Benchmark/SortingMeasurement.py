import AlgoritmiDiOrdinamento
import time
import numpy as np
import copy

#### --- MAKING ROOT PROJECT FOLDER VISIBLE AT SCRIPT LEVEL ---

##
## --- Finding root project folder ---
##     (needed to import settings)
##
import os, sys
projectRoot = ""    

for folderPathIndex in range(len(os.getcwd().split(os.sep))-1):
    projectRoot = os.sep.join(os.getcwd().split(os.sep)[:-folderPathIndex-1])
    if not os.path.exists(os.sep.join([projectRoot, "ROOT_BEACON"])):
        projectRoot = ""
    else:
        break

assert projectRoot != "", "Unable to find project root.\nNo 'ROOT_BEACON' file found at project root level!"


## --- Adding root porject folder to current system path ---
if projectRoot not in sys.path:
    sys.path.insert(1, projectRoot)
    
####                    --- end ---

from Utils import ArraySettings
from Utils import ArrayDataManager
from Utils import SortingSettings
sys.setrecursionlimit(ArraySettings.MAXIMUM_ARRAY_LENGTH+1)

# lambda dict to calculate arguments for each sorting algorithm 
AlgorithmArguments = {
    AlgoritmiDiOrdinamento.InsertionSort.__name__: lambda array: (array, ),
    AlgoritmiDiOrdinamento.QuickSort.__name__: lambda array: (array, 0, len(array)-1),
    AlgoritmiDiOrdinamento.QuickSort3Way.__name__: lambda array: (array, 0, len(array)),
    AlgoritmiDiOrdinamento.CountingSort.__name__: lambda array: (array, [0]*len(array), max(array)+1),
    AlgoritmiDiOrdinamento.RadixSort.__name__: lambda array: (array, len(str(max(array)+1)))
}



class MeasurableTimeExecutionAlgorithm:
    """
    Classe wrapper per la gestione e l'esecuzione di algoritmi misurabili nel tempo.
    Permette di settare una funzione tra quelle disponibili, eseguirla su input forniti e ottenerne nome e riferimento.

    Attributi:
        function (Callable): riferimento alla funzione algoritmica attualmente selezionata.

    Metodi:
        set(function: Callable) -> None:
            Imposta la funzione da usare, verificando che sia tra quelle definite in AlgorithmArguments.
            Solleva un'eccezione se la funzione non è riconosciuta.

        get() -> Callable:
            Ritorna la funzione attualmente impostata.

        get_name() -> str:
            Ritorna il nome (stringa) della funzione attualmente impostata.

        execute(array: Any) -> Any:
            Esegue la funzione impostata sui dati forniti.
            Gli argomenti effettivi vengono determinati dinamicamente tramite `AlgorithmArguments[nome_funzione](array)`.

    Raises:
        Exception: se si tenta di settare una funzione non riconosciuta (non presente in `AlgorithmArguments`).
    """

    # Attributo statico: contiene la funzione corrente (inizialmente None)
    function = None

    def set(self, function):
        """
        Imposta la funzione da utilizzare per le misurazioni.
        Verifica che il nome della funzione sia presente tra quelli riconosciuti in AlgorithmArguments.
        """
        if not function.__name__ in list(AlgorithmArguments.keys()):
            # Solleva errore se la funzione non è tra quelle note
            raise Exception(f"Unknown algorithm {function.__name__}.\nAvaliable algorithms: {list(AlgorithmArguments.keys())}")

        # Salva il riferimento alla funzione da misurare
        self.function = function

    def execute(self, array):
        """
        Esegue la funzione salvata, passando gli argomenti ottenuti dinamicamente da AlgorithmArguments.
        """
        # Prende gli argomenti da passare in base al nome della funzione, poi la esegue
        return self.function(*(AlgorithmArguments[self.get().__name__](array)))

    def get(self):
        """
        Restituisce il riferimento alla funzione attualmente impostata.
        """
        return self.function

    def get_name(self):
        """
        Restituisce il nome della funzione attualmente impostata.
        """
        return self.function.__name__


    
def measure(function: Callable, minTime: float, *args) -> float:
    """
    Misura il tempo medio di esecuzione della funzione `function`, ripetendola più volte finché il tempo totale
    non supera `minTime`.

    Args:
        function (Callable): la funzione da misurare. Deve accettare gli argomenti forniti in `args`.
        minTime (float): tempo minimo cumulativo (in secondi) da raggiungere prima di calcolare la media.
        *args: argomenti posizionali da passare alla funzione in ogni chiamata.

    Returns:
        float: tempo medio (in secondi) per una singola esecuzione della funzione su `args`.
    """

    count = 0  # Contatore del numero di esecuzioni effettuate
    start_time = time.perf_counter()  # Tempo iniziale ad alta risoluzione

    while True:
        function(*args)  # Esegue la funzione con gli argomenti specificati
        end_time = time.perf_counter()  # Tempo dopo l'esecuzione
        count += 1  # Incrementa il numero di ripetizioni

        # Se il tempo cumulativo ha superato minTime, termina il ciclo
        if end_time - start_time >= minTime:
            break

    # Calcola il tempo medio dividendo il tempo totale per il numero di esecuzioni
    return (end_time - start_time) / count



## function to measure sorting time for determinate array chunk
def measure_container_array(array_sample_container: ArraySampleContainer, 
                            function: MeasurableTimeExecutionAlgorithm, 
                            minTime: float = None) -> list[ArrayExecutionTime]:
    """
    Misura i tempi di esecuzione di un algoritmo (function) su ciascun array presente in un oggetto ArraySampleContainer.

    Args:
        array_sample_container (ArraySampleContainer): contenitore di array su cui eseguire le misurazioni.
        function (MeasurableTimeExecutionAlgorithm): wrapper dell'algoritmo da misurare (deve essere già settato).
        minTime (float, opzionale): tempo minimo cumulativo da misurare per ciascun array per ottenere una media stabile.
            Se non specificato, viene determinato tramite `SortingSettings.compute_min_time()`.

    Returns:
        List[ArrayExecutionTime]: lista di oggetti che rappresentano i tempi medi di esecuzione per ciascuna configurazione di array.

    Raises:
        AssertionError: se `array_sample_container` non è un'istanza di `ArraySampleContainer` o se l'integrità della struttura viene alterata durante la misurazione.
    """
    

    # Creano due copie deep dell'array container per confrontare l'integrità e lavorare in sicurezza
    array_sample_container_copy_comparison = copy.deepcopy(array_sample_container)
    array_sample_container_copy = copy.deepcopy(array_sample_container)

    # Se minTime non è specificato, lo si calcola dinamicamente
    if minTime is None:
        minTime = SortingSettings.compute_min_time()
    
    # Primo test rapido per attivare eventuali ottimizzazioni warm-up
    [measure(function, minTime, [i for i in range(100)])]

    # Controllo di tipo: deve essere un ArraySampleContainer
    assert isinstance(array_sample_container, ArrayDataManager.ArraySampleContainer), \
        f"Chunk element expected as ArraySampleContainer, got {type(array_sample_container)}"
    
    array_execution_times = []  # Lista dei risultati temporali

    # Itera su ciascun sample di array
    for array_sample in array_sample_container_copy.get_samples():
        time_repetitions = []

        # Per ogni ripetizione del sample, misura il tempo
        for data in array_sample.get_sample():
            time_repetitions.append(measure(function, minTime, data))

        # Costruisce un oggetto ArrayExecutionTime da ogni sample
        array_execution_times.append(
            ArrayDataManager.ArrayExecutionTime(
                variability = array_sample.get_variability(),
                execution_times = time_repetitions,
                creation_arguments = array_sample.get_creation_arguments()
            )
        )

    # Verifica che la struttura iniziale non sia stata modificata durante la misurazione
    assert ArrayDataManager.deep_compare(array_sample_container.to_dict(), 
                                         array_sample_container_copy_comparison.to_dict()), \
        f"Modification in array structure detected."
    
    return array_execution_times