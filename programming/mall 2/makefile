CC = gcc
CFLAG = -g -Wall
OBJS = queue.o mall.o
TARGET = app
all : $(TARGET)
$(TARGET) : $(OBJS)
	$(CC) -o $@ $(OBJS)
clean:
	rm -f *.o
	rm -f $(TARGET)
