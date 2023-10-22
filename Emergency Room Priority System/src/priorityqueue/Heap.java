package priorityqueue;

import java.util.Comparator;

public class Heap<T> implements PriorityQueueADT<T> {

  private int numElements;
  private T[] heap;
  private boolean isMaxHeap;
  private Comparator<T> comparator;
  private final static int INIT_SIZE = 5;

  /**
   * Constructor for the heap.
   * @param comparator comparator object to define a sorting order for the heap elements.
   * @param isMaxHeap Flag to set if the heap should be a max heap or a min heap.
   */
  public Heap(Comparator<T> comparator, boolean isMaxHeap) {
    //TODO: Implement this method.
    heap = (T[]) new Object[INIT_SIZE];
    this.comparator = comparator;
    this.isMaxHeap = isMaxHeap;
  }

  /**
   * This results in the entry at the specified index "bubbling up" to a location
   * such that the property of the heap are maintained. This method should run in
   * O(log(size)) time.
   * Note: When enqueue is called, an entry is placed at the next available index in 
   * the array and then this method is called on that index. 
   *
   * @param index the index to bubble up
   */
  public void bubbleUp(int index) {
    //TODO: Implement this method.
    T parent = heap[(index - 1) / 2];
    T temp = null;
    if (parent != null) {
      if (compare(parent, heap[index]) < 0) {
        temp = parent;
        heap[(index - 1) / 2] = heap[index];
        heap[index] = temp;
        index = (index - 1) / 2;
        bubbleUp(index);
      }
    }
  }

  /**
   * This method results in the entry at the specified index "bubbling down" to a
   * location such that the property of the heap are maintained. This method
   * should run in O(log(size)) time.
   * Note: When remove is called, if there are elements remaining in this
   *  the bottom most element of the heap is placed at
   * the 0th index and bubbleDown(0) is called.
   * 
   * @param index
   */
  public void bubbleDown(int index) {
    //TODO: Implement this method.
    T leftChild = null;
    T rightChild = null;
    T higherPriorityChild = null;
    T temp = null;
    if (2 * index + 1 < size()) {
      leftChild = heap[2 * index + 1];
    }
    if (2 * index + 2 < size()) {
      rightChild = heap[2 * index + 2];
    }
    if (leftChild != null && rightChild != null) {
      higherPriorityChild = leftChild;
      if (compare(leftChild, rightChild) < 0) {
        higherPriorityChild = rightChild;
      }
      if (higherPriorityChild == leftChild) {
        if (compare(higherPriorityChild, heap[index]) > 0) {
          temp = heap[index];
          heap[index] = heap[2 * index + 1];
          heap[2 * index + 1] = temp;
          index = 2 * index + 1;
          bubbleDown(index);
        }
      }
      else {
        if (compare(higherPriorityChild, heap[index]) > 0) {
          temp = heap[index];
          heap[index] = heap[2 * index + 2];
          heap[2 * index + 2] = temp;
          index = 2 * index + 2;
          bubbleDown(index);
        }
      }
    }
    else if (leftChild != null) {
      if (compare(leftChild, heap[index]) > 0) {
        temp = heap[index];
        heap[index] = heap[2 * index + 1];
        heap[2 * index + 1] = temp;
        index = 2 * index + 1;
        bubbleDown(index);
      }
    }
    else if (rightChild != null) {
      if (compare(rightChild, heap[index]) > 0) {
        temp = heap[index];
        heap[index] = heap[2 * index + 2];
        heap[2 * index + 2] = temp;
        index = 2 * index + 2;
        bubbleDown(index);
      }
    }
  }

  /**
   * Test for if the queue is empty.
   * @return true if queue is empty, false otherwise.
   */
  public boolean isEmpty() {
    boolean isEmpty = false;
    //TODO: Implement this method.
    if (numElements <= 0) {
      isEmpty = true;
    }
    return isEmpty;
  }

  /**
   * Number of data elements in the queue.
   * @return the size
   */
  public int size(){
    int size = -100;
    //TODO: Implement this method.
    size = numElements;
    return size;
  }

  /**
   * Compare method to implement max/min heap behavior.  It calls the comparae method from the 
   * comparator object and multiply its output by 1 and -1 if max and min heap respectively.
   * TODO: implement the heap compare method
   * @param element1 first element to be compared
   * @param element2 second element to be compared
   * @return positive int if {@code element1 > element2}, 0 if {@code element1 == element2}, negative int otherwise
   */
  public int compare(T element1 , T element2) {
    int result = 0;
    int compareSign =  -1;
    if (isMaxHeap) {
      compareSign = 1;
    }
    result = compareSign * comparator.compare(element1, element2);
    return result;
  }

  /**
   * Return the element with highest (or lowest if min heap) priority in the heap 
   * without removing the element.
   * @return T, the top element
   * @throws QueueUnderflowException if empty
   */
  public T peek() throws QueueUnderflowException {
    T data = null;
    //TODO: Implement this method.
    if (isEmpty()) {
      throw new QueueUnderflowException("Calling peek on empty array");
    }
    data = heap[0];
    return data;
  }  

  /**
   * Removes and returns the element with highest (or lowest if min heap) priority in the heap.
   * @return T, the top element
   * @throws QueueUnderflowException if empty
   */
  public T dequeue() throws QueueUnderflowException{
    T data = null;
    //TODO: Implement this method.
    if (isEmpty()) {
      throw new QueueUnderflowException("Calling dequeue on empty array.");
    }
    data = heap[0];
    heap[0] = heap[numElements - 1];
    heap[numElements - 1] = null;
    numElements--;
    bubbleDown(0);
    return data;
  }

  /**
   * Enqueue the element.
   * @param the new element
   */
  public void enqueue(T newElement) {
    //TODO: Implement this method.
    while (numElements >= heap.length) {
      heap = arrayExpand(heap);
    }
    heap[numElements] = newElement;
    bubbleUp(numElements);
    numElements++;
  }

  private T[] arrayExpand(T[] heap) {
    T[] newHeap = (T[]) new Object[2 * heap.length];
    for (int i = 0; i < heap.length; i++) {
      newHeap[i] = heap[i];
    }
    return newHeap;
  }
}