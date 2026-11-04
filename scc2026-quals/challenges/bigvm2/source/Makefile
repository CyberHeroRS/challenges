TARGET = bigvm2
SRCS = src/main.cpp src/vm.cpp src/bigint.cpp

$(TARGET): $(SRCS)
	g++ $(SRCS) -o $(TARGET) -std=c++23
	strip $(TARGET)

clean:
	rm -f $(TARGET)