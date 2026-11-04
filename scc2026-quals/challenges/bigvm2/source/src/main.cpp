#include "vm.hpp"

int main(int argc, char* argv[])
{
    if (argc < 2) {
        std::print("[USAGE]: {} <filename>", argv[0]);
        std::exit(1);
    }
    try {
        VirtualMachine vm;
        vm.init(std::string(argv[1]));
        vm.run();
    }
    catch (const std::runtime_error& err) {
        std::print("ERROR: {}", err.what());
    }
    return 0;
}