import math
import numpy as np
##----------------------------------------------------------------Inserion-------------------------------------------------------------------##

def InsertionSort(A):
    for i in range(1, len(A)):
        key = A[i]
        j = i-1
        while(j > -1 and A[j] > key):
            A[j+1] = A[j]
            j = j - 1
        A[j+1] = key



##----------------------------------------------------------------QuickSort-------------------------------------------------------------------##

def QuickSort(A, p, q):
    if (p < q):
        r = PartitionSlow(A, p, q)
        QuickSort(A, p, r-1)
        QuickSort(A, r+1, q)
    
def PartitionSlow(A, p, q):
    x = A[q]
    i = p-1
    for j in range(p, q):
        if (A[j] <= x):
            i = i+1
            swap(A, i, j)
    swap(A, i+1, q)
    return i+1

def swap(A, i, j):
    x = A[i]
    A[i] = A[j]
    A[j] = x

##----------------------------------------------------------------QuickSort3Way-------------------------------------------------------------------##

def partition3way(a, lo, hi):
    pivot = a[hi - 1]
    lt = lo
    i = lo
    gt = hi - 1

    while i <= gt:
        if a[i] < pivot:
            a[lt], a[i] = a[i], a[lt]
            lt += 1
            i += 1
        elif a[i] > pivot:
            a[i], a[gt] = a[gt], a[i]
            gt -= 1
        else:
            i += 1
    return lt, gt + 1

def QuickSort3Way(a, lo, hi):
    if hi - lo <= 1:
        return

    lt, gt = partition3way(a, lo, hi)
    QuickSort3Way(a, lo, lt)
    QuickSort3Way(a, gt, hi)

##------------------------------------------------------------------------CountingSort--------------------------------------------------------------##

def CountingSort(A, B, k):

    c = [0]*(k)

    assert len(c) == k

    for i in range(0, len(A)):
        assert A[i] < k
        c[A[i]] = c[A[i]]+1


    for j in range(1, k):
        c[j] = c[j] + c[j-1]

    for i in range(len(A)-1, -1, -1):
        B[c[A[i]]-1] = A[i]
        c[A[i]] = c[A[i]]-1
    
#-------------------------------------------------RadixSort-------------------------------------------------------------------------------------------#

def get_digit(num, index):
    result = (num // (10**index)) % 10
    return result

def get_max_digit(array):
    max = 0
    for i in range(0, len(array)):
        if ( (math.floor(math.log10(array[i]+1))+1) > max ):
            max = array[i]
    return max


def CountingSort2(A, B, k, d):

    c = [0]*(k)

    for i in range(0, len(A)):
        c[get_digit(A[i], d)] = c[get_digit(A[i], d)]+1


    for j in range(1, k):
        c[j] = c[j] + c[j-1]
    
    #for i, x in enumerate(c):
        #print(i, x)


    for i in range(len(A)-1, -1, -1):
        B[c[get_digit(A[i], d)]-1] = A[i]
        c[get_digit(A[i], d)] = c[get_digit(A[i], d)]-1
    

## NOT WORKING WITH NEGATIVE NUMBERS
def RadixSort(A, d):
    B = [0]*len(A)
    for i in range(0, d):
        #print("Analysing digits: ", i)
        CountingSort2(A, B, 10, i)
        A = B[:]

    return A

#-------------------------------------------------BucketSort-------------------------------------------------------------------------------------------#

def bucketSort(A):
    B = []
    for i in range(len(A)+1):
        B.append([])

    for i in range(len(A)):
        B[math.floor(A[i]*len(A))].append(A[i])
    
    for i in range(len(A)):
        insertionSort(B[i])

    currentIndex = 0
    for i in range(len(A)):
        for e in range(len(B[i])):
            A[currentIndex] = B[i][e]
            currentIndex+= 1
