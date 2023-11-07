#include <stdlib.h>
#include <stdio.h>
#include <pthread.h>
#include <unistd.h>
#include <semaphore.h>

static sem_t caller_lock; // Semaphore for the caller
static sem_t connected_lock; // Semaphore for the connection
static sem_t operators; // Semaphore for the operators
static int next_id = 1; // Next caller's id
static int NUM_OPERATORS = 4; // The total number of operators
static int NUM_LINES = 7; // Total number of lines
static int connected = 0; // Callers connected at the moment

// Callers making phonecalls
// This is a thread function used for every successfully created thread
// It takes in void *vargp as its argument and returns NULL
void *phonecall (void *vargp) {

   // Assignining each caller an id
   int caller_id;
   sem_wait(&caller_lock);
   caller_id = next_id;
   // Incrementing the id for the next caller
   ++next_id;
   sem_post(&caller_lock);
   // Caller attempting to connect
   printf("Caller %d is attempting to connect...\n", caller_id);
   sem_wait(&connected_lock);
   // Check if the operators are all busy
   while (connected == NUM_LINES) {
      sem_post(&connected_lock);
      // Line is busy
      printf("Line is busy, caller %d attempting to reconnect...\n", caller_id);
      sleep(1);
      sem_wait(&connected_lock);
   }
   // Caller connected to the line
   printf("Caller %d connects to an available line, call ringing...\n", caller_id);
   ++connected;
   sem_post(&connected_lock);
   sleep(1);
   sem_wait(&operators);
   // Connected with an operator and speaking
   printf("Caller %d is speaking to an operator in the local health center.\n", caller_id);
   // Speaking
   sleep(3);
   --connected;
   // Appointment made and operator left
   printf("Caller %d has made an appointment for the test! The operator has left...\n", caller_id);
   // Caller hung up
   printf("Caller %d has hung up!\n", caller_id);
   sem_post(&operators);
   
   return NULL;
}

// argc is the number of arguments and argv is the array of char pointers to the arguments
int main (int argc, char *argv[]) {

   // Check if there are two arguments
   if (argc != 2) {
      printf("Requires two arguments, please enter the correct number of arguments.\n");
      exit(1);
   }
   // Check if the argument is an number or not
   if (atoi(argv[1]) == 0) {
      printf("Please enter an valid integer for the number of phone calls.\n");
      exit(1);
   }
   else {
      // Initializing the semaphores
      sem_init(&caller_lock, 0, 1);
      sem_init(&connected_lock, 0, 1);
      sem_init(&operators, 0, NUM_OPERATORS);
      // Creating threads
      pthread_t threads[atoi(argv[1])];
      for (int i = 0; i < atoi(argv[1]); ++i) {
         int create_thread = pthread_create(&threads[i], 0, phonecall, NULL);
         // Check if the threads are created successfully
         while (create_thread != 0) {
            sleep(1);
            create_thread = pthread_create(&threads[i], 0, phonecall, NULL);
         }
      }
      // Joining the threads
      for (int i = 0; i < atoi(argv[1]); ++i) {
         pthread_join(threads[i], NULL);
      }
   }
   // Destroy the semaphores after all threads exit
   sem_destroy(&caller_lock);
   sem_destroy(&connected_lock);
   sem_destroy(&operators);

   return 0;
}