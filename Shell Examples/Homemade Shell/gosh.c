#include <stddef.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <errno.h>
#include <unistd.h>
#include <sys/wait.h>
#include <sys/types.h>
#include <sys/stat.h>
#include <fcntl.h>
#include <stdbool.h>

int main (int argc, char *argv[]) { 
    bool activeMode = true;
    const char error_message[] = "An error has occurred.\n";
    
    if (argc == 2){ //batch mode
        int fd = open(argv[1], O_RDONLY);
        dup2(fd, STDIN_FILENO);
        close(fd);
        activeMode = false;
    }
    
    else if (argc > 2 ) {
       fprintf(stderr, "ERROR\n");
       exit(EXIT_FAILURE);
    }
    
    while (1){
            bool redirect = false;
            bool useExec = true;
            if (activeMode){
                printf("gosh> ");
            }
            char *line = NULL;
            size_t n = 0;
            ssize_t lineSize = 0;
            lineSize = getline(&line, &n, stdin);
            
            char *dupline = strdup(line);
            
            //ctrl+d exit
            if (lineSize  == -1){
                if (errno == 0){
                    if (activeMode){
                        printf("\n");
                    }
                    exit(0);
                }
            }
            //"exit" exit 
            if (strcmp(line, "exit\n") == 0){
                exit(0);       
            }            
           
            
            char *token;
            int tokenCnt = 0;
            
            //First Pass
            while((token = strsep(&line, " \t\n")) != NULL){
                if (strlen(token) > 0){
                    tokenCnt += 1;
                }
            }
            char **getTokens = malloc((tokenCnt + 2) * sizeof(char *));
            //Second Pass
            tokenCnt = 0;
            int redirectCount = 0;
            bool checkNumFiles = false;
            int countNumFiles = -1;
            char *fileName;
            int redirectEnd;
            
            while((token = strsep(&dupline, " \t\n")) != NULL){
                if (strlen(token) > 0){
                    getTokens[tokenCnt] = token;
                    
                    //printf("%s",token);
                    
                    if (strcmp(token, ">") == 0){
                        redirectCount += 1;
                        checkNumFiles = true;
                        redirectEnd = tokenCnt;
                    }
                    if (checkNumFiles){
                        countNumFiles++;
                        fileName = token;
                        
                    }
                    tokenCnt += 1;
                    
                }
            }   
            if (redirectCount > 0){
                if (redirectCount == 1 && countNumFiles == 1){
                    redirect = true;
                    
                } //else if(redirectCount > 1){
                else{
                    
                    fprintf(stderr, error_message);  
                    useExec = false;
                }/*else if (countNumFiles > 1){
                    printf("An error has occured.\n");
                    useExec = false;
                }*/
            }

            
            getTokens[tokenCnt] = "\n";
            getTokens[tokenCnt + 1] = NULL;
            
            int i = 0;
            char *myargs[80];
            
            //parse  
            while(1){               
                if (strcmp(getTokens[i], "&") == 0){
                    myargs[i] = NULL;
                    
                }else if (strcmp(getTokens[i], "\n")==0){
                    myargs[i] = NULL;
                    myargs[i+1] = NULL;
                    break;
                }else{
                    myargs[i] = strdup(getTokens[i]);  
                }
                i += 1;
            }
            i = 0;
            
            pid_t rc;
            int status = 0;
            
            if(strcmp(myargs[0], "cd")==0){
                useExec = false;
                if(myargs[1] == NULL){
                    if (chdir(getenv("HOME")) != 0){
                        fprintf(stderr, error_message);  
                    } 
                                
                }else if (myargs[2] != NULL){
                        fprintf(stderr, error_message);  
                }else{
                    if(chdir(myargs[1]) != 0){
                        fprintf(stderr, error_message);  
                    }
                }
                
            }

            while(useExec){
                rc = fork();
 
                if (rc < 0) { // fork failed; exit
                    fprintf(stderr, "fork failed\n");
                    exit(1);
                } else if (rc == 0) { // child
                    if (redirect){
                        myargs[redirectEnd] = NULL;
                        int fd = open(fileName, O_TRUNC | O_WRONLY | O_CREAT, S_IRUSR| S_IWUSR);
                        dup2(fd, 1);
                        close(fd);
                    }

                    execvp(myargs[i], &myargs[i]);
                    
                    //const char error_message[] = "An error has occurred.\n";
                    fprintf(stderr, error_message);  
                    exit(1);
                    
                } else { // parent
                    //increment i to execute next function
                    while(1){
                        if (myargs[i] == NULL){
                            //goto next function                            
                            i += 1;
                            break;
                        }
                        i += 1;    
                    }
                    
                    //if no functions left
                    if (myargs[i] == NULL){
                        //waiting for final process
                        while (rc != wait(&status));
                        break;
                    }
                }
                  
           }
            
        } 
    
    return 0; 
}



