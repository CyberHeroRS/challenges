
#include <iostream>
#include <fstream>

#define ull unsigned long long

void printFlag() {
    std::ifstream file("flag.txt");
    std::string line;
    std::getline(file, line);
    std::cout << line << std::endl;
    exit(0);
}

class Node {
    private:
        ull val;
    public:
        ~Node() {}
        Node(ull val) : val(val) {}
        ull getVal() { return val; }
};

class Vertex: public Node {
    public:
        Vertex(ull val) : Node(val) {}
        virtual Vertex* handle() = 0;
};

class Edge: public Node {
    public:
        Edge(ull val) : Node(val) {}
        virtual Vertex* next(ull curr) = 0;
};
class E0: public Edge {
    private: ull getX() { return 892; }
    public:
        E0(ull val) : Edge(val) {}
        Vertex *next(ull curr) override;
};
class E1: public Edge {
    private: ull getX() { return 388; }
    public:
        E1(ull val) : Edge(val) {}
        Vertex *next(ull curr) override;
};
class E2: public Edge {
    private: ull getX() { return 459; }
    public:
        E2(ull val) : Edge(val) {}
        Vertex *next(ull curr) override;
};
class E3: public Edge {
    private: ull getX() { return 130; }
    public:
        E3(ull val) : Edge(val) {}
        Vertex *next(ull curr) override;
};
class E4: public Edge {
    private: ull getX() { return 992; }
    public:
        E4(ull val) : Edge(val) {}
        Vertex *next(ull curr) override;
};
class E5: public Edge {
    private: ull getX() { return 556; }
    public:
        E5(ull val) : Edge(val) {}
        Vertex *next(ull curr) override;
};
class E6: public Edge {
    private: ull getX() { return 842; }
    public:
        E6(ull val) : Edge(val) {}
        Vertex *next(ull curr) override;
};
class E7: public Edge {
    private: ull getX() { return 701; }
    public:
        E7(ull val) : Edge(val) {}
        Vertex *next(ull curr) override;
};
class E8: public Edge {
    private: ull getX() { return 897; }
    public:
        E8(ull val) : Edge(val) {}
        Vertex *next(ull curr) override;
};
class E9: public Edge {
    private: ull getX() { return 896; }
    public:
        E9(ull val) : Edge(val) {}
        Vertex *next(ull curr) override;
};
class E10: public Edge {
    private: ull getX() { return 144; }
    public:
        E10(ull val) : Edge(val) {}
        Vertex *next(ull curr) override;
};
class E11: public Edge {
    private: ull getX() { return 185; }
    public:
        E11(ull val) : Edge(val) {}
        Vertex *next(ull curr) override;
};
class E12: public Edge {
    private: ull getX() { return 341; }
    public:
        E12(ull val) : Edge(val) {}
        Vertex *next(ull curr) override;
};
class E13: public Edge {
    private: ull getX() { return 680; }
    public:
        E13(ull val) : Edge(val) {}
        Vertex *next(ull curr) override;
};
class E14: public Edge {
    private: ull getX() { return 193; }
    public:
        E14(ull val) : Edge(val) {}
        Vertex *next(ull curr) override;
};
class E15: public Edge {
    private: ull getX() { return 474; }
    public:
        E15(ull val) : Edge(val) {}
        Vertex *next(ull curr) override;
};
class E16: public Edge {
    private: ull getX() { return 406; }
    public:
        E16(ull val) : Edge(val) {}
        Vertex *next(ull curr) override;
};
class E17: public Edge {
    private: ull getX() { return 985; }
    public:
        E17(ull val) : Edge(val) {}
        Vertex *next(ull curr) override;
};
class E18: public Edge {
    private: ull getX() { return 881; }
    public:
        E18(ull val) : Edge(val) {}
        Vertex *next(ull curr) override;
};
class E19: public Edge {
    private: ull getX() { return 729; }
    public:
        E19(ull val) : Edge(val) {}
        Vertex *next(ull curr) override;
};
class E20: public Edge {
    private: ull getX() { return 175; }
    public:
        E20(ull val) : Edge(val) {}
        Vertex *next(ull curr) override;
};
class E21: public Edge {
    private: ull getX() { return 107; }
    public:
        E21(ull val) : Edge(val) {}
        Vertex *next(ull curr) override;
};
class E22: public Edge {
    private: ull getX() { return 926; }
    public:
        E22(ull val) : Edge(val) {}
        Vertex *next(ull curr) override;
};
class E23: public Edge {
    private: ull getX() { return 909; }
    public:
        E23(ull val) : Edge(val) {}
        Vertex *next(ull curr) override;
};
class E24: public Edge {
    private: ull getX() { return 840; }
    public:
        E24(ull val) : Edge(val) {}
        Vertex *next(ull curr) override;
};
class E25: public Edge {
    private: ull getX() { return 385; }
    public:
        E25(ull val) : Edge(val) {}
        Vertex *next(ull curr) override;
};
class E26: public Edge {
    private: ull getX() { return 206; }
    public:
        E26(ull val) : Edge(val) {}
        Vertex *next(ull curr) override;
};
class E27: public Edge {
    private: ull getX() { return 85; }
    public:
        E27(ull val) : Edge(val) {}
        Vertex *next(ull curr) override;
};
class E28: public Edge {
    private: ull getX() { return 621; }
    public:
        E28(ull val) : Edge(val) {}
        Vertex *next(ull curr) override;
};
class E29: public Edge {
    private: ull getX() { return 8; }
    public:
        E29(ull val) : Edge(val) {}
        Vertex *next(ull curr) override;
};
class E30: public Edge {
    private: ull getX() { return 524; }
    public:
        E30(ull val) : Edge(val) {}
        Vertex *next(ull curr) override;
};
class E31: public Edge {
    private: ull getX() { return 629; }
    public:
        E31(ull val) : Edge(val) {}
        Vertex *next(ull curr) override;
};
class E32: public Edge {
    private: ull getX() { return 730; }
    public:
        E32(ull val) : Edge(val) {}
        Vertex *next(ull curr) override;
};
class E33: public Edge {
    private: ull getX() { return 333; }
    public:
        E33(ull val) : Edge(val) {}
        Vertex *next(ull curr) override;
};
class E34: public Edge {
    private: ull getX() { return 307; }
    public:
        E34(ull val) : Edge(val) {}
        Vertex *next(ull curr) override;
};
class E35: public Edge {
    private: ull getX() { return 803; }
    public:
        E35(ull val) : Edge(val) {}
        Vertex *next(ull curr) override;
};
class E36: public Edge {
    private: ull getX() { return 577; }
    public:
        E36(ull val) : Edge(val) {}
        Vertex *next(ull curr) override;
};
class E37: public Edge {
    private: ull getX() { return 336; }
    public:
        E37(ull val) : Edge(val) {}
        Vertex *next(ull curr) override;
};
class E38: public Edge {
    private: ull getX() { return 442; }
    public:
        E38(ull val) : Edge(val) {}
        Vertex *next(ull curr) override;
};
class E39: public Edge {
    private: ull getX() { return 139; }
    public:
        E39(ull val) : Edge(val) {}
        Vertex *next(ull curr) override;
};
class E40: public Edge {
    private: ull getX() { return 674; }
    public:
        E40(ull val) : Edge(val) {}
        Vertex *next(ull curr) override;
};
class E41: public Edge {
    private: ull getX() { return 937; }
    public:
        E41(ull val) : Edge(val) {}
        Vertex *next(ull curr) override;
};
class E42: public Edge {
    private: ull getX() { return 694; }
    public:
        E42(ull val) : Edge(val) {}
        Vertex *next(ull curr) override;
};
class E43: public Edge {
    private: ull getX() { return 658; }
    public:
        E43(ull val) : Edge(val) {}
        Vertex *next(ull curr) override;
};
class E44: public Edge {
    private: ull getX() { return 646; }
    public:
        E44(ull val) : Edge(val) {}
        Vertex *next(ull curr) override;
};
class E45: public Edge {
    private: ull getX() { return 218; }
    public:
        E45(ull val) : Edge(val) {}
        Vertex *next(ull curr) override;
};
class E46: public Edge {
    private: ull getX() { return 264; }
    public:
        E46(ull val) : Edge(val) {}
        Vertex *next(ull curr) override;
};
class E47: public Edge {
    private: ull getX() { return 392; }
    public:
        E47(ull val) : Edge(val) {}
        Vertex *next(ull curr) override;
};
class E48: public Edge {
    private: ull getX() { return 964; }
    public:
        E48(ull val) : Edge(val) {}
        Vertex *next(ull curr) override;
};
class E49: public Edge {
    private: ull getX() { return 16; }
    public:
        E49(ull val) : Edge(val) {}
        Vertex *next(ull curr) override;
};
class E50: public Edge {
    private: ull getX() { return 832; }
    public:
        E50(ull val) : Edge(val) {}
        Vertex *next(ull curr) override;
};
class E51: public Edge {
    private: ull getX() { return 289; }
    public:
        E51(ull val) : Edge(val) {}
        Vertex *next(ull curr) override;
};
class E52: public Edge {
    private: ull getX() { return 550; }
    public:
        E52(ull val) : Edge(val) {}
        Vertex *next(ull curr) override;
};
class E53: public Edge {
    private: ull getX() { return 88; }
    public:
        E53(ull val) : Edge(val) {}
        Vertex *next(ull curr) override;
};
class E54: public Edge {
    private: ull getX() { return 479; }
    public:
        E54(ull val) : Edge(val) {}
        Vertex *next(ull curr) override;
};
class E55: public Edge {
    private: ull getX() { return 339; }
    public:
        E55(ull val) : Edge(val) {}
        Vertex *next(ull curr) override;
};
class E56: public Edge {
    private: ull getX() { return 431; }
    public:
        E56(ull val) : Edge(val) {}
        Vertex *next(ull curr) override;
};
class E57: public Edge {
    private: ull getX() { return 467; }
    public:
        E57(ull val) : Edge(val) {}
        Vertex *next(ull curr) override;
};
class E58: public Edge {
    private: ull getX() { return 564; }
    public:
        E58(ull val) : Edge(val) {}
        Vertex *next(ull curr) override;
};
class E59: public Edge {
    private: ull getX() { return 370; }
    public:
        E59(ull val) : Edge(val) {}
        Vertex *next(ull curr) override;
};
class E60: public Edge {
    private: ull getX() { return 284; }
    public:
        E60(ull val) : Edge(val) {}
        Vertex *next(ull curr) override;
};
class E61: public Edge {
    private: ull getX() { return 476; }
    public:
        E61(ull val) : Edge(val) {}
        Vertex *next(ull curr) override;
};
class E62: public Edge {
    private: ull getX() { return 731; }
    public:
        E62(ull val) : Edge(val) {}
        Vertex *next(ull curr) override;
};
class E63: public Edge {
    private: ull getX() { return 75; }
    public:
        E63(ull val) : Edge(val) {}
        Vertex *next(ull curr) override;
};
class E64: public Edge {
    private: ull getX() { return 235; }
    public:
        E64(ull val) : Edge(val) {}
        Vertex *next(ull curr) override;
};
class E65: public Edge {
    private: ull getX() { return 781; }
    public:
        E65(ull val) : Edge(val) {}
        Vertex *next(ull curr) override;
};
class E66: public Edge {
    private: ull getX() { return 631; }
    public:
        E66(ull val) : Edge(val) {}
        Vertex *next(ull curr) override;
};
class E67: public Edge {
    private: ull getX() { return 153; }
    public:
        E67(ull val) : Edge(val) {}
        Vertex *next(ull curr) override;
};
class E68: public Edge {
    private: ull getX() { return 662; }
    public:
        E68(ull val) : Edge(val) {}
        Vertex *next(ull curr) override;
};
class E69: public Edge {
    private: ull getX() { return 541; }
    public:
        E69(ull val) : Edge(val) {}
        Vertex *next(ull curr) override;
};
class E70: public Edge {
    private: ull getX() { return 146; }
    public:
        E70(ull val) : Edge(val) {}
        Vertex *next(ull curr) override;
};
class E71: public Edge {
    private: ull getX() { return 492; }
    public:
        E71(ull val) : Edge(val) {}
        Vertex *next(ull curr) override;
};
class E72: public Edge {
    private: ull getX() { return 318; }
    public:
        E72(ull val) : Edge(val) {}
        Vertex *next(ull curr) override;
};
class E73: public Edge {
    private: ull getX() { return 672; }
    public:
        E73(ull val) : Edge(val) {}
        Vertex *next(ull curr) override;
};
class E74: public Edge {
    private: ull getX() { return 853; }
    public:
        E74(ull val) : Edge(val) {}
        Vertex *next(ull curr) override;
};
class E75: public Edge {
    private: ull getX() { return 609; }
    public:
        E75(ull val) : Edge(val) {}
        Vertex *next(ull curr) override;
};
class E76: public Edge {
    private: ull getX() { return 756; }
    public:
        E76(ull val) : Edge(val) {}
        Vertex *next(ull curr) override;
};
class E77: public Edge {
    private: ull getX() { return 929; }
    public:
        E77(ull val) : Edge(val) {}
        Vertex *next(ull curr) override;
};
class E78: public Edge {
    private: ull getX() { return 97; }
    public:
        E78(ull val) : Edge(val) {}
        Vertex *next(ull curr) override;
};
class E79: public Edge {
    private: ull getX() { return 536; }
    public:
        E79(ull val) : Edge(val) {}
        Vertex *next(ull curr) override;
};
class E80: public Edge {
    private: ull getX() { return 648; }
    public:
        E80(ull val) : Edge(val) {}
        Vertex *next(ull curr) override;
};
class E81: public Edge {
    private: ull getX() { return 19; }
    public:
        E81(ull val) : Edge(val) {}
        Vertex *next(ull curr) override;
};
class E82: public Edge {
    private: ull getX() { return 346; }
    public:
        E82(ull val) : Edge(val) {}
        Vertex *next(ull curr) override;
};
class E83: public Edge {
    private: ull getX() { return 659; }
    public:
        E83(ull val) : Edge(val) {}
        Vertex *next(ull curr) override;
};
class E84: public Edge {
    private: ull getX() { return 540; }
    public:
        E84(ull val) : Edge(val) {}
        Vertex *next(ull curr) override;
};
class E85: public Edge {
    private: ull getX() { return 7; }
    public:
        E85(ull val) : Edge(val) {}
        Vertex *next(ull curr) override;
};
class E86: public Edge {
    private: ull getX() { return 108; }
    public:
        E86(ull val) : Edge(val) {}
        Vertex *next(ull curr) override;
};
class E87: public Edge {
    private: ull getX() { return 487; }
    public:
        E87(ull val) : Edge(val) {}
        Vertex *next(ull curr) override;
};
class E88: public Edge {
    private: ull getX() { return 74; }
    public:
        E88(ull val) : Edge(val) {}
        Vertex *next(ull curr) override;
};
class E89: public Edge {
    private: ull getX() { return 485; }
    public:
        E89(ull val) : Edge(val) {}
        Vertex *next(ull curr) override;
};
class E90: public Edge {
    private: ull getX() { return 547; }
    public:
        E90(ull val) : Edge(val) {}
        Vertex *next(ull curr) override;
};
class E91: public Edge {
    private: ull getX() { return 293; }
    public:
        E91(ull val) : Edge(val) {}
        Vertex *next(ull curr) override;
};
class E92: public Edge {
    private: ull getX() { return 939; }
    public:
        E92(ull val) : Edge(val) {}
        Vertex *next(ull curr) override;
};
class E93: public Edge {
    private: ull getX() { return 805; }
    public:
        E93(ull val) : Edge(val) {}
        Vertex *next(ull curr) override;
};
class E94: public Edge {
    private: ull getX() { return 379; }
    public:
        E94(ull val) : Edge(val) {}
        Vertex *next(ull curr) override;
};
class E95: public Edge {
    private: ull getX() { return 116; }
    public:
        E95(ull val) : Edge(val) {}
        Vertex *next(ull curr) override;
};
class E96: public Edge {
    private: ull getX() { return 538; }
    public:
        E96(ull val) : Edge(val) {}
        Vertex *next(ull curr) override;
};
class E97: public Edge {
    private: ull getX() { return 60; }
    public:
        E97(ull val) : Edge(val) {}
        Vertex *next(ull curr) override;
};
class E98: public Edge {
    private: ull getX() { return 984; }
    public:
        E98(ull val) : Edge(val) {}
        Vertex *next(ull curr) override;
};
class E99: public Edge {
    private: ull getX() { return 520; }
    public:
        E99(ull val) : Edge(val) {}
        Vertex *next(ull curr) override;
};
class V0: public Vertex, E17, E19, E5{
    public:
        V0(ull val) : Vertex(val), E17(4), E19(3), E5(5){}
    Vertex *handle() {
        Edge *e;
        switch (getchar()) {
    case '0': e = static_cast<E17*>(this);break;case '1': e = static_cast<E19*>(this);break;case '2': e = static_cast<E5*>(this);break;default: return this;
    }
    return e->next(static_cast<Vertex*>(this)->getVal());
    }};class V1: public Vertex, E15, E13, E7{
    public:
        V1(ull val) : Vertex(val), E15(4), E13(2), E7(3){}
    Vertex *handle() {
        Edge *e;
        switch (getchar()) {
    case '0': e = static_cast<E15*>(this);break;case '1': e = static_cast<E13*>(this);break;case '2': e = static_cast<E7*>(this);break;default: return this;
    }
    return e->next(static_cast<Vertex*>(this)->getVal());
    }};class V2: public Vertex, E5, E7, E12, E13, E18, E19, E20{
    public:
        V2(ull val) : Vertex(val), E5(5), E7(6), E12(8), E13(13), E18(7), E19(9), E20(3){}
    Vertex *handle() {
        Edge *e;
        switch (getchar()) {
    case '0': e = static_cast<E5*>(this);break;case '1': e = static_cast<E7*>(this);break;case '2': e = static_cast<E12*>(this);break;case '3': e = static_cast<E13*>(this);break;case '4': e = static_cast<E18*>(this);break;case '5': e = static_cast<E19*>(this);break;case '6': e = static_cast<E20*>(this);break;default: return this;
    }
    return e->next(static_cast<Vertex*>(this)->getVal());
    }};class V3: public Vertex, E8, E11, E12, E15{
    public:
        V3(ull val) : Vertex(val), E8(7), E11(5), E12(4), E15(2){}
    Vertex *handle() {
        Edge *e;
        switch (getchar()) {
    case '0': e = static_cast<E8*>(this);break;case '1': e = static_cast<E11*>(this);break;case '2': e = static_cast<E12*>(this);break;case '3': e = static_cast<E15*>(this);break;default: return this;
    }
    return e->next(static_cast<Vertex*>(this)->getVal());
    }};class V4: public Vertex, E6, E7, E9, E12, E16, E17, E19{
    public:
        V4(ull val) : Vertex(val), E6(11), E7(13), E9(12), E12(4), E16(6), E17(3), E19(5){}
    Vertex *handle() {
        Edge *e;
        switch (getchar()) {
    case '0': e = static_cast<E6*>(this);break;case '1': e = static_cast<E7*>(this);break;case '2': e = static_cast<E9*>(this);break;case '3': e = static_cast<E12*>(this);break;case '4': e = static_cast<E16*>(this);break;case '5': e = static_cast<E17*>(this);break;case '6': e = static_cast<E19*>(this);break;default: return this;
    }
    return e->next(static_cast<Vertex*>(this)->getVal());
    }};class V5: public Vertex, E11, E12, E13{
    public:
        V5(ull val) : Vertex(val), E11(2), E12(3), E13(4){}
    Vertex *handle() {
        Edge *e;
        switch (getchar()) {
    case '0': e = static_cast<E11*>(this);break;case '1': e = static_cast<E12*>(this);break;case '2': e = static_cast<E13*>(this);break;default: return this;
    }
    return e->next(static_cast<Vertex*>(this)->getVal());
    }};class V6: public Vertex, E16, E24, E23, E7{
    public:
        V6(ull val) : Vertex(val), E16(2), E24(4), E23(5), E7(7){}
    Vertex *handle() {
        Edge *e;
        switch (getchar()) {
    case '0': e = static_cast<E16*>(this);break;case '1': e = static_cast<E24*>(this);break;case '2': e = static_cast<E23*>(this);break;case '3': e = static_cast<E7*>(this);break;default: return this;
    }
    return e->next(static_cast<Vertex*>(this)->getVal());
    }};class V7: public Vertex, E0, E1, E2, E4, E6, E8, E11{
    public:
        V7(ull val) : Vertex(val), E0(9), E1(3), E2(8), E4(5), E6(10), E8(2), E11(11){}
    Vertex *handle() {
        Edge *e;
        switch (getchar()) {
    case '0': e = static_cast<E0*>(this);break;case '1': e = static_cast<E1*>(this);break;case '2': e = static_cast<E2*>(this);break;case '3': e = static_cast<E4*>(this);break;case '4': e = static_cast<E6*>(this);break;case '5': e = static_cast<E8*>(this);break;case '6': e = static_cast<E11*>(this);break;default: return this;
    }
    return e->next(static_cast<Vertex*>(this)->getVal());
    }};class V8: public Vertex, E0, E2, E3, E5, E6, E14{
    public:
        V8(ull val) : Vertex(val), E0(5), E2(9), E3(6), E5(11), E6(8), E14(10){}
    Vertex *handle() {
        Edge *e;
        switch (getchar()) {
    case '0': e = static_cast<E0*>(this);break;case '1': e = static_cast<E2*>(this);break;case '2': e = static_cast<E3*>(this);break;case '3': e = static_cast<E5*>(this);break;case '4': e = static_cast<E6*>(this);break;case '5': e = static_cast<E14*>(this);break;default: return this;
    }
    return e->next(static_cast<Vertex*>(this)->getVal());
    }};class V9: public Vertex, E1, E5, E6, E7, E14{
    public:
        V9(ull val) : Vertex(val), E1(5), E5(8), E6(7), E7(6), E14(9){}
    Vertex *handle() {
        Edge *e;
        switch (getchar()) {
    case '0': e = static_cast<E1*>(this);break;case '1': e = static_cast<E5*>(this);break;case '2': e = static_cast<E6*>(this);break;case '3': e = static_cast<E7*>(this);break;case '4': e = static_cast<E14*>(this);break;default: return this;
    }
    return e->next(static_cast<Vertex*>(this)->getVal());
    }};class V10: public Vertex, E0, E1, E2, E3, E5, E6, E7, E8, E18{
    public:
        V10(ull val) : Vertex(val), E0(9), E1(11), E2(10), E3(13), E5(16), E6(14), E7(17), E8(6), E18(15){}
    Vertex *handle() {
        Edge *e;
        switch (getchar()) {
    case '0': e = static_cast<E0*>(this);break;case '1': e = static_cast<E1*>(this);break;case '2': e = static_cast<E2*>(this);break;case '3': e = static_cast<E3*>(this);break;case '4': e = static_cast<E5*>(this);break;case '5': e = static_cast<E6*>(this);break;case '6': e = static_cast<E7*>(this);break;case '7': e = static_cast<E8*>(this);break;case '8': e = static_cast<E18*>(this);break;default: return this;
    }
    return e->next(static_cast<Vertex*>(this)->getVal());
    }};class V11: public Vertex, E0, E2, E3, E4, E6, E7, E8, E10{
    public:
        V11(ull val) : Vertex(val), E0(10), E2(2), E3(9), E4(8), E6(11), E7(5), E8(4), E10(13){}
    Vertex *handle() {
        Edge *e;
        switch (getchar()) {
    case '0': e = static_cast<E0*>(this);break;case '1': e = static_cast<E2*>(this);break;case '2': e = static_cast<E3*>(this);break;case '3': e = static_cast<E4*>(this);break;case '4': e = static_cast<E6*>(this);break;case '5': e = static_cast<E7*>(this);break;case '6': e = static_cast<E8*>(this);break;case '7': e = static_cast<E10*>(this);break;default: return this;
    }
    return e->next(static_cast<Vertex*>(this)->getVal());
    }};class V12: public Vertex, E0, E4, E6, E7, E9, E10, E11, E15{
    public:
        V12(ull val) : Vertex(val), E0(11), E4(9), E6(6), E7(13), E9(5), E10(4), E11(14), E15(7){}
    Vertex *handle() {
        Edge *e;
        switch (getchar()) {
    case '0': e = static_cast<E0*>(this);break;case '1': e = static_cast<E4*>(this);break;case '2': e = static_cast<E6*>(this);break;case '3': e = static_cast<E7*>(this);break;case '4': e = static_cast<E9*>(this);break;case '5': e = static_cast<E10*>(this);break;case '6': e = static_cast<E11*>(this);break;case '7': e = static_cast<E15*>(this);break;default: return this;
    }
    return e->next(static_cast<Vertex*>(this)->getVal());
    }};class V13: public Vertex, E1, E3, E4, E7, E8, E9, E12{
    public:
        V13(ull val) : Vertex(val), E1(10), E3(13), E4(12), E7(9), E8(7), E9(6), E12(8){}
    Vertex *handle() {
        Edge *e;
        switch (getchar()) {
    case '0': e = static_cast<E1*>(this);break;case '1': e = static_cast<E3*>(this);break;case '2': e = static_cast<E4*>(this);break;case '3': e = static_cast<E7*>(this);break;case '4': e = static_cast<E8*>(this);break;case '5': e = static_cast<E9*>(this);break;case '6': e = static_cast<E12*>(this);break;default: return this;
    }
    return e->next(static_cast<Vertex*>(this)->getVal());
    }};class V14: public Vertex, E4, E6, E8, E10, E11, E13{
    public:
        V14(ull val) : Vertex(val), E4(9), E6(6), E8(4), E10(3), E11(8), E13(5){}
    Vertex *handle() {
        Edge *e;
        switch (getchar()) {
    case '0': e = static_cast<E4*>(this);break;case '1': e = static_cast<E6*>(this);break;case '2': e = static_cast<E8*>(this);break;case '3': e = static_cast<E10*>(this);break;case '4': e = static_cast<E11*>(this);break;case '5': e = static_cast<E13*>(this);break;default: return this;
    }
    return e->next(static_cast<Vertex*>(this)->getVal());
    }};class V15: public Vertex, E0, E6, E7, E14, E19, E20, E21{
    public:
        V15(ull val) : Vertex(val), E0(3), E6(9), E7(7), E14(5), E19(2), E20(8), E21(6){}
    Vertex *handle() {
        Edge *e;
        switch (getchar()) {
    case '0': e = static_cast<E0*>(this);break;case '1': e = static_cast<E6*>(this);break;case '2': e = static_cast<E7*>(this);break;case '3': e = static_cast<E14*>(this);break;case '4': e = static_cast<E19*>(this);break;case '5': e = static_cast<E20*>(this);break;case '6': e = static_cast<E21*>(this);break;default: return this;
    }
    return e->next(static_cast<Vertex*>(this)->getVal());
    }};class V16: public Vertex, E0, E6, E7, E10, E17, E21{
    public:
        V16(ull val) : Vertex(val), E0(4), E6(10), E7(3), E10(2), E17(5), E21(6){}
    Vertex *handle() {
        Edge *e;
        switch (getchar()) {
    case '0': e = static_cast<E0*>(this);break;case '1': e = static_cast<E6*>(this);break;case '2': e = static_cast<E7*>(this);break;case '3': e = static_cast<E10*>(this);break;case '4': e = static_cast<E17*>(this);break;case '5': e = static_cast<E21*>(this);break;default: return this;
    }
    return e->next(static_cast<Vertex*>(this)->getVal());
    }};class V17: public Vertex, E0, E10, E4, E15{
    public:
        V17(ull val) : Vertex(val), E0(4), E10(6), E4(3), E15(2){}
    Vertex *handle() {
        Edge *e;
        switch (getchar()) {
    case '0': e = static_cast<E0*>(this);break;case '1': e = static_cast<E10*>(this);break;case '2': e = static_cast<E4*>(this);break;case '3': e = static_cast<E15*>(this);break;default: return this;
    }
    return e->next(static_cast<Vertex*>(this)->getVal());
    }};class V18: public Vertex, E7, E10, E12, E13, E14, E16, E26{
    public:
        V18(ull val) : Vertex(val), E7(3), E10(4), E12(6), E13(5), E14(10), E16(2), E26(7){}
    Vertex *handle() {
        Edge *e;
        switch (getchar()) {
    case '0': e = static_cast<E7*>(this);break;case '1': e = static_cast<E10*>(this);break;case '2': e = static_cast<E12*>(this);break;case '3': e = static_cast<E13*>(this);break;case '4': e = static_cast<E14*>(this);break;case '5': e = static_cast<E16*>(this);break;case '6': e = static_cast<E26*>(this);break;default: return this;
    }
    return e->next(static_cast<Vertex*>(this)->getVal());
    }};class V19: public Vertex, E17, E10, E5{
    public:
        V19(ull val) : Vertex(val), E17(4), E10(3), E5(2){}
    Vertex *handle() {
        Edge *e;
        switch (getchar()) {
    case '0': e = static_cast<E17*>(this);break;case '1': e = static_cast<E10*>(this);break;case '2': e = static_cast<E5*>(this);break;default: return this;
    }
    return e->next(static_cast<Vertex*>(this)->getVal());
    }};class V20: public Vertex, E0, E4, E10, E16, E19, E28{
    public:
        V20(ull val) : Vertex(val), E0(5), E4(11), E10(7), E16(10), E19(4), E28(6){}
    Vertex *handle() {
        Edge *e;
        switch (getchar()) {
    case '0': e = static_cast<E0*>(this);break;case '1': e = static_cast<E4*>(this);break;case '2': e = static_cast<E10*>(this);break;case '3': e = static_cast<E16*>(this);break;case '4': e = static_cast<E19*>(this);break;case '5': e = static_cast<E28*>(this);break;default: return this;
    }
    return e->next(static_cast<Vertex*>(this)->getVal());
    }};class V21: public Vertex, E1, E5, E7, E8, E11, E26{
    public:
        V21(ull val) : Vertex(val), E1(9), E5(10), E7(5), E8(7), E11(2), E26(6){}
    Vertex *handle() {
        Edge *e;
        switch (getchar()) {
    case '0': e = static_cast<E1*>(this);break;case '1': e = static_cast<E5*>(this);break;case '2': e = static_cast<E7*>(this);break;case '3': e = static_cast<E8*>(this);break;case '4': e = static_cast<E11*>(this);break;case '5': e = static_cast<E26*>(this);break;default: return this;
    }
    return e->next(static_cast<Vertex*>(this)->getVal());
    }};class V22: public Vertex, E3, E6, E7, E9, E14, E15, E18, E24, E31{
    public:
        V22(ull val) : Vertex(val), E3(11), E6(4), E7(14), E9(16), E14(12), E15(3), E18(8), E24(2), E31(13){}
    Vertex *handle() {
        Edge *e;
        switch (getchar()) {
    case '0': e = static_cast<E3*>(this);break;case '1': e = static_cast<E6*>(this);break;case '2': e = static_cast<E7*>(this);break;case '3': e = static_cast<E9*>(this);break;case '4': e = static_cast<E14*>(this);break;case '5': e = static_cast<E15*>(this);break;case '6': e = static_cast<E18*>(this);break;case '7': e = static_cast<E24*>(this);break;case '8': e = static_cast<E31*>(this);break;default: return this;
    }
    return e->next(static_cast<Vertex*>(this)->getVal());
    }};class V23: public Vertex, E7, E12, E17, E19, E26{
    public:
        V23(ull val) : Vertex(val), E7(6), E12(4), E17(8), E19(2), E26(5){}
    Vertex *handle() {
        Edge *e;
        switch (getchar()) {
    case '0': e = static_cast<E7*>(this);break;case '1': e = static_cast<E12*>(this);break;case '2': e = static_cast<E17*>(this);break;case '3': e = static_cast<E19*>(this);break;case '4': e = static_cast<E26*>(this);break;default: return this;
    }
    return e->next(static_cast<Vertex*>(this)->getVal());
    }};class V24: public Vertex, E6, E11, E14, E22, E23{
    public:
        V24(ull val) : Vertex(val), E6(4), E11(7), E14(8), E22(5), E23(6){}
    Vertex *handle() {
        Edge *e;
        switch (getchar()) {
    case '0': e = static_cast<E6*>(this);break;case '1': e = static_cast<E11*>(this);break;case '2': e = static_cast<E14*>(this);break;case '3': e = static_cast<E22*>(this);break;case '4': e = static_cast<E23*>(this);break;default: return this;
    }
    return e->next(static_cast<Vertex*>(this)->getVal());
    }};class V25: public Vertex, E0, E1, E3, E27, E28{
    public:
        V25(ull val) : Vertex(val), E0(4), E1(2), E3(6), E27(3), E28(7){}
    Vertex *handle() {
        Edge *e;
        switch (getchar()) {
    case '0': e = static_cast<E0*>(this);break;case '1': e = static_cast<E1*>(this);break;case '2': e = static_cast<E3*>(this);break;case '3': e = static_cast<E27*>(this);break;case '4': e = static_cast<E28*>(this);break;default: return this;
    }
    return e->next(static_cast<Vertex*>(this)->getVal());
    }};class V26: public Vertex, E33, E10, E21, E25{
    public:
        V26(ull val) : Vertex(val), E33(3), E10(4), E21(5), E25(7){}
    Vertex *handle() {
        Edge *e;
        switch (getchar()) {
    case '0': e = static_cast<E33*>(this);break;case '1': e = static_cast<E10*>(this);break;case '2': e = static_cast<E21*>(this);break;case '3': e = static_cast<E25*>(this);break;default: return this;
    }
    return e->next(static_cast<Vertex*>(this)->getVal());
    }};class V27: public Vertex, E34, E7, E13, E23{
    public:
        V27(ull val) : Vertex(val), E34(4), E7(7), E13(2), E23(6){}
    Vertex *handle() {
        Edge *e;
        switch (getchar()) {
    case '0': e = static_cast<E34*>(this);break;case '1': e = static_cast<E7*>(this);break;case '2': e = static_cast<E13*>(this);break;case '3': e = static_cast<E23*>(this);break;default: return this;
    }
    return e->next(static_cast<Vertex*>(this)->getVal());
    }};class V28: public Vertex, E1, E2, E6, E8, E12, E16, E25{
    public:
        V28(ull val) : Vertex(val), E1(7), E2(3), E6(8), E8(11), E12(2), E16(9), E25(4){}
    Vertex *handle() {
        Edge *e;
        switch (getchar()) {
    case '0': e = static_cast<E1*>(this);break;case '1': e = static_cast<E2*>(this);break;case '2': e = static_cast<E6*>(this);break;case '3': e = static_cast<E8*>(this);break;case '4': e = static_cast<E12*>(this);break;case '5': e = static_cast<E16*>(this);break;case '6': e = static_cast<E25*>(this);break;default: return this;
    }
    return e->next(static_cast<Vertex*>(this)->getVal());
    }};class V29: public Vertex, E33, E4, E10, E12, E14, E21, E24{
    public:
        V29(ull val) : Vertex(val), E33(11), E4(13), E10(8), E12(12), E14(4), E21(9), E24(3){}
    Vertex *handle() {
        Edge *e;
        switch (getchar()) {
    case '0': e = static_cast<E33*>(this);break;case '1': e = static_cast<E4*>(this);break;case '2': e = static_cast<E10*>(this);break;case '3': e = static_cast<E12*>(this);break;case '4': e = static_cast<E14*>(this);break;case '5': e = static_cast<E21*>(this);break;case '6': e = static_cast<E24*>(this);break;default: return this;
    }
    return e->next(static_cast<Vertex*>(this)->getVal());
    }};class V30: public Vertex, E35, E27, E28, E14{
    public:
        V30(ull val) : Vertex(val), E35(7), E27(2), E28(4), E14(6){}
    Vertex *handle() {
        Edge *e;
        switch (getchar()) {
    case '0': e = static_cast<E35*>(this);break;case '1': e = static_cast<E27*>(this);break;case '2': e = static_cast<E28*>(this);break;case '3': e = static_cast<E14*>(this);break;default: return this;
    }
    return e->next(static_cast<Vertex*>(this)->getVal());
    }};class V31: public Vertex, E3, E9, E20, E21, E26, E27{
    public:
        V31(ull val) : Vertex(val), E3(2), E9(11), E20(9), E21(3), E26(8), E27(5){}
    Vertex *handle() {
        Edge *e;
        switch (getchar()) {
    case '0': e = static_cast<E3*>(this);break;case '1': e = static_cast<E9*>(this);break;case '2': e = static_cast<E20*>(this);break;case '3': e = static_cast<E21*>(this);break;case '4': e = static_cast<E26*>(this);break;case '5': e = static_cast<E27*>(this);break;default: return this;
    }
    return e->next(static_cast<Vertex*>(this)->getVal());
    }};class V32: public Vertex, E33, E6, E7, E15, E16, E25, E26, E30{
    public:
        V32(ull val) : Vertex(val), E33(8), E6(9), E7(13), E15(15), E16(11), E25(14), E26(7), E30(12){}
    Vertex *handle() {
        Edge *e;
        switch (getchar()) {
    case '0': e = static_cast<E33*>(this);break;case '1': e = static_cast<E6*>(this);break;case '2': e = static_cast<E7*>(this);break;case '3': e = static_cast<E15*>(this);break;case '4': e = static_cast<E16*>(this);break;case '5': e = static_cast<E25*>(this);break;case '6': e = static_cast<E26*>(this);break;case '7': e = static_cast<E30*>(this);break;default: return this;
    }
    return e->next(static_cast<Vertex*>(this)->getVal());
    }};class V33: public Vertex, E1, E40, E16, E28, E30{
    public:
        V33(ull val) : Vertex(val), E1(6), E40(4), E16(2), E28(7), E30(3){}
    Vertex *handle() {
        Edge *e;
        switch (getchar()) {
    case '0': e = static_cast<E1*>(this);break;case '1': e = static_cast<E40*>(this);break;case '2': e = static_cast<E16*>(this);break;case '3': e = static_cast<E28*>(this);break;case '4': e = static_cast<E30*>(this);break;default: return this;
    }
    return e->next(static_cast<Vertex*>(this)->getVal());
    }};class V34: public Vertex, E37, E8, E20, E21, E22, E25{
    public:
        V34(ull val) : Vertex(val), E37(10), E8(2), E20(8), E21(5), E22(6), E25(3){}
    Vertex *handle() {
        Edge *e;
        switch (getchar()) {
    case '0': e = static_cast<E37*>(this);break;case '1': e = static_cast<E8*>(this);break;case '2': e = static_cast<E20*>(this);break;case '3': e = static_cast<E21*>(this);break;case '4': e = static_cast<E22*>(this);break;case '5': e = static_cast<E25*>(this);break;default: return this;
    }
    return e->next(static_cast<Vertex*>(this)->getVal());
    }};class V35: public Vertex, E2, E37, E8, E11, E20, E28, E30{
    public:
        V35(ull val) : Vertex(val), E2(13), E37(8), E8(6), E11(10), E20(12), E28(7), E30(11){}
    Vertex *handle() {
        Edge *e;
        switch (getchar()) {
    case '0': e = static_cast<E2*>(this);break;case '1': e = static_cast<E37*>(this);break;case '2': e = static_cast<E8*>(this);break;case '3': e = static_cast<E11*>(this);break;case '4': e = static_cast<E20*>(this);break;case '5': e = static_cast<E28*>(this);break;case '6': e = static_cast<E30*>(this);break;default: return this;
    }
    return e->next(static_cast<Vertex*>(this)->getVal());
    }};class V36: public Vertex, E33, E3, E43, E12, E20, E26, E27, E28{
    public:
        V36(ull val) : Vertex(val), E33(13), E3(11), E43(8), E12(7), E20(3), E26(14), E27(6), E28(9){}
    Vertex *handle() {
        Edge *e;
        switch (getchar()) {
    case '0': e = static_cast<E33*>(this);break;case '1': e = static_cast<E3*>(this);break;case '2': e = static_cast<E43*>(this);break;case '3': e = static_cast<E12*>(this);break;case '4': e = static_cast<E20*>(this);break;case '5': e = static_cast<E26*>(this);break;case '6': e = static_cast<E27*>(this);break;case '7': e = static_cast<E28*>(this);break;default: return this;
    }
    return e->next(static_cast<Vertex*>(this)->getVal());
    }};class V37: public Vertex, E1, E34, E35, E44, E21, E28, E29, E31{
    public:
        V37(ull val) : Vertex(val), E1(8), E34(9), E35(14), E44(12), E21(3), E28(10), E29(13), E31(11){}
    Vertex *handle() {
        Edge *e;
        switch (getchar()) {
    case '0': e = static_cast<E1*>(this);break;case '1': e = static_cast<E34*>(this);break;case '2': e = static_cast<E35*>(this);break;case '3': e = static_cast<E44*>(this);break;case '4': e = static_cast<E21*>(this);break;case '5': e = static_cast<E28*>(this);break;case '6': e = static_cast<E29*>(this);break;case '7': e = static_cast<E31*>(this);break;default: return this;
    }
    return e->next(static_cast<Vertex*>(this)->getVal());
    }};class V38: public Vertex, E35, E36, E37, E44, E16, E20, E26, E28, E30{
    public:
        V38(ull val) : Vertex(val), E35(17), E36(10), E37(4), E44(5), E16(8), E20(11), E26(7), E28(15), E30(2){}
    Vertex *handle() {
        Edge *e;
        switch (getchar()) {
    case '0': e = static_cast<E35*>(this);break;case '1': e = static_cast<E36*>(this);break;case '2': e = static_cast<E37*>(this);break;case '3': e = static_cast<E44*>(this);break;case '4': e = static_cast<E16*>(this);break;case '5': e = static_cast<E20*>(this);break;case '6': e = static_cast<E26*>(this);break;case '7': e = static_cast<E28*>(this);break;case '8': e = static_cast<E30*>(this);break;default: return this;
    }
    return e->next(static_cast<Vertex*>(this)->getVal());
    }};class V39: public Vertex, E35, E9, E11, E43, E16, E23, E28{
    public:
        V39(ull val) : Vertex(val), E35(12), E9(9), E11(8), E43(6), E16(5), E23(2), E28(3){}
    Vertex *handle() {
        Edge *e;
        switch (getchar()) {
    case '0': e = static_cast<E35*>(this);break;case '1': e = static_cast<E9*>(this);break;case '2': e = static_cast<E11*>(this);break;case '3': e = static_cast<E43*>(this);break;case '4': e = static_cast<E16*>(this);break;case '5': e = static_cast<E23*>(this);break;case '6': e = static_cast<E28*>(this);break;default: return this;
    }
    return e->next(static_cast<Vertex*>(this)->getVal());
    }};class V40: public Vertex, E1, E35, E8, E11, E23, E28, E30{
    public:
        V40(ull val) : Vertex(val), E1(7), E35(13), E8(11), E11(9), E23(4), E28(5), E30(8){}
    Vertex *handle() {
        Edge *e;
        switch (getchar()) {
    case '0': e = static_cast<E1*>(this);break;case '1': e = static_cast<E35*>(this);break;case '2': e = static_cast<E8*>(this);break;case '3': e = static_cast<E11*>(this);break;case '4': e = static_cast<E23*>(this);break;case '5': e = static_cast<E28*>(this);break;case '6': e = static_cast<E30*>(this);break;default: return this;
    }
    return e->next(static_cast<Vertex*>(this)->getVal());
    }};class V41: public Vertex, E4, E37, E42, E46, E14, E18{
    public:
        V41(ull val) : Vertex(val), E4(3), E37(8), E42(2), E46(6), E14(4), E18(5){}
    Vertex *handle() {
        Edge *e;
        switch (getchar()) {
    case '0': e = static_cast<E4*>(this);break;case '1': e = static_cast<E37*>(this);break;case '2': e = static_cast<E42*>(this);break;case '3': e = static_cast<E46*>(this);break;case '4': e = static_cast<E14*>(this);break;case '5': e = static_cast<E18*>(this);break;default: return this;
    }
    return e->next(static_cast<Vertex*>(this)->getVal());
    }};class V42: public Vertex, E38, E6, E41, E44, E47, E16, E26{
    public:
        V42(ull val) : Vertex(val), E38(5), E6(12), E41(2), E44(6), E47(11), E16(10), E26(13){}
    Vertex *handle() {
        Edge *e;
        switch (getchar()) {
    case '0': e = static_cast<E38*>(this);break;case '1': e = static_cast<E6*>(this);break;case '2': e = static_cast<E41*>(this);break;case '3': e = static_cast<E44*>(this);break;case '4': e = static_cast<E47*>(this);break;case '5': e = static_cast<E16*>(this);break;case '6': e = static_cast<E26*>(this);break;default: return this;
    }
    return e->next(static_cast<Vertex*>(this)->getVal());
    }};class V43: public Vertex, E34, E35, E8, E10, E11, E47, E16, E29{
    public:
        V43(ull val) : Vertex(val), E34(8), E35(13), E8(5), E10(6), E11(3), E47(12), E16(4), E29(15){}
    Vertex *handle() {
        Edge *e;
        switch (getchar()) {
    case '0': e = static_cast<E34*>(this);break;case '1': e = static_cast<E35*>(this);break;case '2': e = static_cast<E8*>(this);break;case '3': e = static_cast<E10*>(this);break;case '4': e = static_cast<E11*>(this);break;case '5': e = static_cast<E47*>(this);break;case '6': e = static_cast<E16*>(this);break;case '7': e = static_cast<E29*>(this);break;default: return this;
    }
    return e->next(static_cast<Vertex*>(this)->getVal());
    }};class V44: public Vertex, E33, E36, E5, E42, E10, E13, E18, E29{
    public:
        V44(ull val) : Vertex(val), E33(4), E36(14), E5(9), E42(8), E10(10), E13(2), E18(3), E29(15){}
    Vertex *handle() {
        Edge *e;
        switch (getchar()) {
    case '0': e = static_cast<E33*>(this);break;case '1': e = static_cast<E36*>(this);break;case '2': e = static_cast<E5*>(this);break;case '3': e = static_cast<E42*>(this);break;case '4': e = static_cast<E10*>(this);break;case '5': e = static_cast<E13*>(this);break;case '6': e = static_cast<E18*>(this);break;case '7': e = static_cast<E29*>(this);break;default: return this;
    }
    return e->next(static_cast<Vertex*>(this)->getVal());
    }};class V45: public Vertex, E32, E36, E43, E13, E14, E18, E20{
    public:
        V45(ull val) : Vertex(val), E32(2), E36(3), E43(9), E13(4), E14(12), E18(7), E20(5){}
    Vertex *handle() {
        Edge *e;
        switch (getchar()) {
    case '0': e = static_cast<E32*>(this);break;case '1': e = static_cast<E36*>(this);break;case '2': e = static_cast<E43*>(this);break;case '3': e = static_cast<E13*>(this);break;case '4': e = static_cast<E14*>(this);break;case '5': e = static_cast<E18*>(this);break;case '6': e = static_cast<E20*>(this);break;default: return this;
    }
    return e->next(static_cast<Vertex*>(this)->getVal());
    }};class V46: public Vertex, E1, E33, E38, E8, E42, E44, E52, E22{
    public:
        V46(ull val) : Vertex(val), E1(13), E33(5), E38(14), E8(10), E42(15), E44(12), E52(7), E22(8){}
    Vertex *handle() {
        Edge *e;
        switch (getchar()) {
    case '0': e = static_cast<E1*>(this);break;case '1': e = static_cast<E33*>(this);break;case '2': e = static_cast<E38*>(this);break;case '3': e = static_cast<E8*>(this);break;case '4': e = static_cast<E42*>(this);break;case '5': e = static_cast<E44*>(this);break;case '6': e = static_cast<E52*>(this);break;case '7': e = static_cast<E22*>(this);break;default: return this;
    }
    return e->next(static_cast<Vertex*>(this)->getVal());
    }};class V47: public Vertex, E16, E41, E44, E25{
    public:
        V47(ull val) : Vertex(val), E16(3), E41(5), E44(6), E25(2){}
    Vertex *handle() {
        Edge *e;
        switch (getchar()) {
    case '0': e = static_cast<E16*>(this);break;case '1': e = static_cast<E41*>(this);break;case '2': e = static_cast<E44*>(this);break;case '3': e = static_cast<E25*>(this);break;default: return this;
    }
    return e->next(static_cast<Vertex*>(this)->getVal());
    }};class V48: public Vertex, E3, E35, E41, E17, E50, E22, E56, E24, E28{
    public:
        V48(ull val) : Vertex(val), E3(14), E35(13), E41(6), E17(11), E50(17), E22(16), E56(12), E24(3), E28(8){}
    Vertex *handle() {
        Edge *e;
        switch (getchar()) {
    case '0': e = static_cast<E3*>(this);break;case '1': e = static_cast<E35*>(this);break;case '2': e = static_cast<E41*>(this);break;case '3': e = static_cast<E17*>(this);break;case '4': e = static_cast<E50*>(this);break;case '5': e = static_cast<E22*>(this);break;case '6': e = static_cast<E56*>(this);break;case '7': e = static_cast<E24*>(this);break;case '8': e = static_cast<E28*>(this);break;default: return this;
    }
    return e->next(static_cast<Vertex*>(this)->getVal());
    }};class V49: public Vertex, E10, E14, E47, E18, E51, E56, E28{
    public:
        V49(ull val) : Vertex(val), E10(10), E14(7), E47(4), E18(9), E51(8), E56(12), E28(6){}
    Vertex *handle() {
        Edge *e;
        switch (getchar()) {
    case '0': e = static_cast<E10*>(this);break;case '1': e = static_cast<E14*>(this);break;case '2': e = static_cast<E47*>(this);break;case '3': e = static_cast<E18*>(this);break;case '4': e = static_cast<E51*>(this);break;case '5': e = static_cast<E56*>(this);break;case '6': e = static_cast<E28*>(this);break;default: return this;
    }
    return e->next(static_cast<Vertex*>(this)->getVal());
    }};class V50: public Vertex, E39, E41, E12, E15, E21, E57{
    public:
        V50(ull val) : Vertex(val), E39(8), E41(10), E12(5), E15(2), E21(7), E57(4){}
    Vertex *handle() {
        Edge *e;
        switch (getchar()) {
    case '0': e = static_cast<E39*>(this);break;case '1': e = static_cast<E41*>(this);break;case '2': e = static_cast<E12*>(this);break;case '3': e = static_cast<E15*>(this);break;case '4': e = static_cast<E21*>(this);break;case '5': e = static_cast<E57*>(this);break;default: return this;
    }
    return e->next(static_cast<Vertex*>(this)->getVal());
    }};class V51: public Vertex, E34, E36, E39, E12, E48, E49, E58{
    public:
        V51(ull val) : Vertex(val), E34(6), E36(4), E39(7), E12(8), E48(12), E49(11), E58(10){}
    Vertex *handle() {
        Edge *e;
        switch (getchar()) {
    case '0': e = static_cast<E34*>(this);break;case '1': e = static_cast<E36*>(this);break;case '2': e = static_cast<E39*>(this);break;case '3': e = static_cast<E12*>(this);break;case '4': e = static_cast<E48*>(this);break;case '5': e = static_cast<E49*>(this);break;case '6': e = static_cast<E58*>(this);break;default: return this;
    }
    return e->next(static_cast<Vertex*>(this)->getVal());
    }};class V52: public Vertex, E34, E3, E37, E40, E42, E44, E56{
    public:
        V52(ull val) : Vertex(val), E34(7), E3(12), E37(10), E40(5), E42(13), E44(9), E56(11){}
    Vertex *handle() {
        Edge *e;
        switch (getchar()) {
    case '0': e = static_cast<E34*>(this);break;case '1': e = static_cast<E3*>(this);break;case '2': e = static_cast<E37*>(this);break;case '3': e = static_cast<E40*>(this);break;case '4': e = static_cast<E42*>(this);break;case '5': e = static_cast<E44*>(this);break;case '6': e = static_cast<E56*>(this);break;default: return this;
    }
    return e->next(static_cast<Vertex*>(this)->getVal());
    }};class V53: public Vertex, E44, E15, E51, E52, E56, E60{
    public:
        V53(ull val) : Vertex(val), E44(7), E15(6), E51(9), E52(8), E56(10), E60(3){}
    Vertex *handle() {
        Edge *e;
        switch (getchar()) {
    case '0': e = static_cast<E44*>(this);break;case '1': e = static_cast<E15*>(this);break;case '2': e = static_cast<E51*>(this);break;case '3': e = static_cast<E52*>(this);break;case '4': e = static_cast<E56*>(this);break;case '5': e = static_cast<E60*>(this);break;default: return this;
    }
    return e->next(static_cast<Vertex*>(this)->getVal());
    }};class V54: public Vertex, E2, E4, E13, E47, E52, E61, E62{
    public:
        V54(ull val) : Vertex(val), E2(2), E4(6), E13(11), E47(12), E52(10), E61(5), E62(7){}
    Vertex *handle() {
        Edge *e;
        switch (getchar()) {
    case '0': e = static_cast<E2*>(this);break;case '1': e = static_cast<E4*>(this);break;case '2': e = static_cast<E13*>(this);break;case '3': e = static_cast<E47*>(this);break;case '4': e = static_cast<E52*>(this);break;case '5': e = static_cast<E61*>(this);break;case '6': e = static_cast<E62*>(this);break;default: return this;
    }
    return e->next(static_cast<Vertex*>(this)->getVal());
    }};class V55: public Vertex, E7, E43, E45, E13, E47, E52, E22, E56{
    public:
        V55(ull val) : Vertex(val), E7(4), E43(14), E45(3), E13(10), E47(8), E52(7), E22(9), E56(15){}
    Vertex *handle() {
        Edge *e;
        switch (getchar()) {
    case '0': e = static_cast<E7*>(this);break;case '1': e = static_cast<E43*>(this);break;case '2': e = static_cast<E45*>(this);break;case '3': e = static_cast<E13*>(this);break;case '4': e = static_cast<E47*>(this);break;case '5': e = static_cast<E52*>(this);break;case '6': e = static_cast<E22*>(this);break;case '7': e = static_cast<E56*>(this);break;default: return this;
    }
    return e->next(static_cast<Vertex*>(this)->getVal());
    }};class V56: public Vertex, E34, E7, E11, E53, E55{
    public:
        V56(ull val) : Vertex(val), E34(6), E7(2), E11(5), E53(8), E55(4){}
    Vertex *handle() {
        Edge *e;
        switch (getchar()) {
    case '0': e = static_cast<E34*>(this);break;case '1': e = static_cast<E7*>(this);break;case '2': e = static_cast<E11*>(this);break;case '3': e = static_cast<E53*>(this);break;case '4': e = static_cast<E55*>(this);break;default: return this;
    }
    return e->next(static_cast<Vertex*>(this)->getVal());
    }};class V57: public Vertex, E38, E10, E46, E51, E53, E63{
    public:
        V57(ull val) : Vertex(val), E38(6), E10(4), E46(8), E51(10), E53(9), E63(5){}
    Vertex *handle() {
        Edge *e;
        switch (getchar()) {
    case '0': e = static_cast<E38*>(this);break;case '1': e = static_cast<E10*>(this);break;case '2': e = static_cast<E46*>(this);break;case '3': e = static_cast<E51*>(this);break;case '4': e = static_cast<E53*>(this);break;case '5': e = static_cast<E63*>(this);break;default: return this;
    }
    return e->next(static_cast<Vertex*>(this)->getVal());
    }};class V58: public Vertex, E43, E49, E53, E59, E60, E29{
    public:
        V58(ull val) : Vertex(val), E43(4), E49(6), E53(7), E59(8), E60(9), E29(2){}
    Vertex *handle() {
        Edge *e;
        switch (getchar()) {
    case '0': e = static_cast<E43*>(this);break;case '1': e = static_cast<E49*>(this);break;case '2': e = static_cast<E53*>(this);break;case '3': e = static_cast<E59*>(this);break;case '4': e = static_cast<E60*>(this);break;case '5': e = static_cast<E29*>(this);break;default: return this;
    }
    return e->next(static_cast<Vertex*>(this)->getVal());
    }};class V59: public Vertex, E3, E38, E50, E21, E55{
    public:
        V59(ull val) : Vertex(val), E3(2), E38(6), E50(9), E21(4), E55(3){}
    Vertex *handle() {
        Edge *e;
        switch (getchar()) {
    case '0': e = static_cast<E3*>(this);break;case '1': e = static_cast<E38*>(this);break;case '2': e = static_cast<E50*>(this);break;case '3': e = static_cast<E21*>(this);break;case '4': e = static_cast<E55*>(this);break;default: return this;
    }
    return e->next(static_cast<Vertex*>(this)->getVal());
    }};class V60: public Vertex, E64, E38, E40, E45, E46, E47, E53{
    public:
        V60(ull val) : Vertex(val), E64(4), E38(12), E40(6), E45(7), E46(10), E47(8), E53(13){}
    Vertex *handle() {
        Edge *e;
        switch (getchar()) {
    case '0': e = static_cast<E64*>(this);break;case '1': e = static_cast<E38*>(this);break;case '2': e = static_cast<E40*>(this);break;case '3': e = static_cast<E45*>(this);break;case '4': e = static_cast<E46*>(this);break;case '5': e = static_cast<E47*>(this);break;case '6': e = static_cast<E53*>(this);break;default: return this;
    }
    return e->next(static_cast<Vertex*>(this)->getVal());
    }};class V61: public Vertex, E4, E8, E14, E17, E51, E20, E26, E60{
    public:
        V61(ull val) : Vertex(val), E4(2), E8(12), E14(7), E17(15), E51(6), E20(11), E26(5), E60(13){}
    Vertex *handle() {
        Edge *e;
        switch (getchar()) {
    case '0': e = static_cast<E4*>(this);break;case '1': e = static_cast<E8*>(this);break;case '2': e = static_cast<E14*>(this);break;case '3': e = static_cast<E17*>(this);break;case '4': e = static_cast<E51*>(this);break;case '5': e = static_cast<E20*>(this);break;case '6': e = static_cast<E26*>(this);break;case '7': e = static_cast<E60*>(this);break;default: return this;
    }
    return e->next(static_cast<Vertex*>(this)->getVal());
    }};class V62: public Vertex, E57, E18, E68, E6{
    public:
        V62(ull val) : Vertex(val), E57(6), E18(4), E68(3), E6(7){}
    Vertex *handle() {
        Edge *e;
        switch (getchar()) {
    case '0': e = static_cast<E57*>(this);break;case '1': e = static_cast<E18*>(this);break;case '2': e = static_cast<E68*>(this);break;case '3': e = static_cast<E6*>(this);break;default: return this;
    }
    return e->next(static_cast<Vertex*>(this)->getVal());
    }};class V63: public Vertex, E3, E38, E72, E8, E11, E48, E55, E58, E29{
    public:
        V63(ull val) : Vertex(val), E3(4), E38(15), E72(3), E8(5), E11(9), E48(12), E55(2), E58(16), E29(10){}
    Vertex *handle() {
        Edge *e;
        switch (getchar()) {
    case '0': e = static_cast<E3*>(this);break;case '1': e = static_cast<E38*>(this);break;case '2': e = static_cast<E72*>(this);break;case '3': e = static_cast<E8*>(this);break;case '4': e = static_cast<E11*>(this);break;case '5': e = static_cast<E48*>(this);break;case '6': e = static_cast<E55*>(this);break;case '7': e = static_cast<E58*>(this);break;case '8': e = static_cast<E29*>(this);break;default: return this;
    }
    return e->next(static_cast<Vertex*>(this)->getVal());
    }};class V64: public Vertex, E37, E40, E46, E24, E59, E61{
    public:
        V64(ull val) : Vertex(val), E37(10), E40(9), E46(3), E24(5), E59(11), E61(8){}
    Vertex *handle() {
        Edge *e;
        switch (getchar()) {
    case '0': e = static_cast<E37*>(this);break;case '1': e = static_cast<E40*>(this);break;case '2': e = static_cast<E46*>(this);break;case '3': e = static_cast<E24*>(this);break;case '4': e = static_cast<E59*>(this);break;case '5': e = static_cast<E61*>(this);break;default: return this;
    }
    return e->next(static_cast<Vertex*>(this)->getVal());
    }};class V65: public Vertex, E0, E66, E35, E12, E50, E56, E28{
    public:
        V65(ull val) : Vertex(val), E0(8), E66(9), E35(2), E12(4), E50(5), E56(11), E28(12){}
    Vertex *handle() {
        Edge *e;
        switch (getchar()) {
    case '0': e = static_cast<E0*>(this);break;case '1': e = static_cast<E66*>(this);break;case '2': e = static_cast<E35*>(this);break;case '3': e = static_cast<E12*>(this);break;case '4': e = static_cast<E50*>(this);break;case '5': e = static_cast<E56*>(this);break;case '6': e = static_cast<E28*>(this);break;default: return this;
    }
    return e->next(static_cast<Vertex*>(this)->getVal());
    }};class V66: public Vertex, E64, E1, E69, E40, E47, E53, E56, E58{
    public:
        V66(ull val) : Vertex(val), E64(12), E1(11), E69(5), E40(9), E47(8), E53(6), E56(10), E58(14){}
    Vertex *handle() {
        Edge *e;
        switch (getchar()) {
    case '0': e = static_cast<E64*>(this);break;case '1': e = static_cast<E1*>(this);break;case '2': e = static_cast<E69*>(this);break;case '3': e = static_cast<E40*>(this);break;case '4': e = static_cast<E47*>(this);break;case '5': e = static_cast<E53*>(this);break;case '6': e = static_cast<E56*>(this);break;case '7': e = static_cast<E58*>(this);break;default: return this;
    }
    return e->next(static_cast<Vertex*>(this)->getVal());
    }};class V67: public Vertex, E69, E7, E75, E15, E16, E59, E60{
    public:
        V67(ull val) : Vertex(val), E69(7), E7(2), E75(4), E15(8), E16(10), E59(11), E60(9){}
    Vertex *handle() {
        Edge *e;
        switch (getchar()) {
    case '0': e = static_cast<E69*>(this);break;case '1': e = static_cast<E7*>(this);break;case '2': e = static_cast<E75*>(this);break;case '3': e = static_cast<E15*>(this);break;case '4': e = static_cast<E16*>(this);break;case '5': e = static_cast<E59*>(this);break;case '6': e = static_cast<E60*>(this);break;default: return this;
    }
    return e->next(static_cast<Vertex*>(this)->getVal());
    }};class V68: public Vertex, E67, E76, E54, E7{
    public:
        V68(ull val) : Vertex(val), E67(5), E76(4), E54(6), E7(2){}
    Vertex *handle() {
        Edge *e;
        switch (getchar()) {
    case '0': e = static_cast<E67*>(this);break;case '1': e = static_cast<E76*>(this);break;case '2': e = static_cast<E54*>(this);break;case '3': e = static_cast<E7*>(this);break;default: return this;
    }
    return e->next(static_cast<Vertex*>(this)->getVal());
    }};class V69: public Vertex, E64, E36, E8, E9, E60, E31{
    public:
        V69(ull val) : Vertex(val), E64(4), E36(6), E8(11), E9(5), E60(7), E31(8){}
    Vertex *handle() {
        Edge *e;
        switch (getchar()) {
    case '0': e = static_cast<E64*>(this);break;case '1': e = static_cast<E36*>(this);break;case '2': e = static_cast<E8*>(this);break;case '3': e = static_cast<E9*>(this);break;case '4': e = static_cast<E60*>(this);break;case '5': e = static_cast<E31*>(this);break;default: return this;
    }
    return e->next(static_cast<Vertex*>(this)->getVal());
    }};class V70: public Vertex, E1, E68, E69, E6, E76, E31{
    public:
        V70(ull val) : Vertex(val), E1(9), E68(11), E69(4), E6(2), E76(8), E31(6){}
    Vertex *handle() {
        Edge *e;
        switch (getchar()) {
    case '0': e = static_cast<E1*>(this);break;case '1': e = static_cast<E68*>(this);break;case '2': e = static_cast<E69*>(this);break;case '3': e = static_cast<E6*>(this);break;case '4': e = static_cast<E76*>(this);break;case '5': e = static_cast<E31*>(this);break;default: return this;
    }
    return e->next(static_cast<Vertex*>(this)->getVal());
    }};class V71: public Vertex, E64, E18, E4, E63{
    public:
        V71(ull val) : Vertex(val), E64(3), E18(2), E4(4), E63(7){}
    Vertex *handle() {
        Edge *e;
        switch (getchar()) {
    case '0': e = static_cast<E64*>(this);break;case '1': e = static_cast<E18*>(this);break;case '2': e = static_cast<E4*>(this);break;case '3': e = static_cast<E63*>(this);break;default: return this;
    }
    return e->next(static_cast<Vertex*>(this)->getVal());
    }};class V72: public Vertex, E64, E69, E41, E10, E45, E54, E25, E26, E63{
    public:
        V72(ull val) : Vertex(val), E64(6), E69(9), E41(2), E10(4), E45(13), E54(15), E25(17), E26(10), E63(3){}
    Vertex *handle() {
        Edge *e;
        switch (getchar()) {
    case '0': e = static_cast<E64*>(this);break;case '1': e = static_cast<E69*>(this);break;case '2': e = static_cast<E41*>(this);break;case '3': e = static_cast<E10*>(this);break;case '4': e = static_cast<E45*>(this);break;case '5': e = static_cast<E54*>(this);break;case '6': e = static_cast<E25*>(this);break;case '7': e = static_cast<E26*>(this);break;case '8': e = static_cast<E63*>(this);break;default: return this;
    }
    return e->next(static_cast<Vertex*>(this)->getVal());
    }};class V73: public Vertex, E7, E71, E9, E74, E12, E47, E55, E30{
    public:
        V73(ull val) : Vertex(val), E7(5), E71(9), E9(12), E74(3), E12(8), E47(15), E55(4), E30(7){}
    Vertex *handle() {
        Edge *e;
        switch (getchar()) {
    case '0': e = static_cast<E7*>(this);break;case '1': e = static_cast<E71*>(this);break;case '2': e = static_cast<E9*>(this);break;case '3': e = static_cast<E74*>(this);break;case '4': e = static_cast<E12*>(this);break;case '5': e = static_cast<E47*>(this);break;case '6': e = static_cast<E55*>(this);break;case '7': e = static_cast<E30*>(this);break;default: return this;
    }
    return e->next(static_cast<Vertex*>(this)->getVal());
    }};class V74: public Vertex, E66, E49, E82, E53, E31{
    public:
        V74(ull val) : Vertex(val), E66(9), E49(2), E82(7), E53(3), E31(8){}
    Vertex *handle() {
        Edge *e;
        switch (getchar()) {
    case '0': e = static_cast<E66*>(this);break;case '1': e = static_cast<E49*>(this);break;case '2': e = static_cast<E82*>(this);break;case '3': e = static_cast<E53*>(this);break;case '4': e = static_cast<E31*>(this);break;default: return this;
    }
    return e->next(static_cast<Vertex*>(this)->getVal());
    }};class V75: public Vertex, E33, E71, E76, E13, E54{
    public:
        V75(ull val) : Vertex(val), E33(2), E71(6), E76(8), E13(3), E54(9){}
    Vertex *handle() {
        Edge *e;
        switch (getchar()) {
    case '0': e = static_cast<E33*>(this);break;case '1': e = static_cast<E71*>(this);break;case '2': e = static_cast<E76*>(this);break;case '3': e = static_cast<E13*>(this);break;case '4': e = static_cast<E54*>(this);break;default: return this;
    }
    return e->next(static_cast<Vertex*>(this)->getVal());
    }};class V76: public Vertex, E64, E37, E39, E79, E24, E59{
    public:
        V76(ull val) : Vertex(val), E64(11), E37(9), E39(4), E79(10), E24(8), E59(7){}
    Vertex *handle() {
        Edge *e;
        switch (getchar()) {
    case '0': e = static_cast<E64*>(this);break;case '1': e = static_cast<E37*>(this);break;case '2': e = static_cast<E39*>(this);break;case '3': e = static_cast<E79*>(this);break;case '4': e = static_cast<E24*>(this);break;case '5': e = static_cast<E59*>(this);break;default: return this;
    }
    return e->next(static_cast<Vertex*>(this)->getVal());
    }};class V77: public Vertex, E39, E71, E45, E79, E49, E83, E84, E28{
    public:
        V77(ull val) : Vertex(val), E39(2), E71(14), E45(3), E79(4), E49(11), E83(6), E84(9), E28(13){}
    Vertex *handle() {
        Edge *e;
        switch (getchar()) {
    case '0': e = static_cast<E39*>(this);break;case '1': e = static_cast<E71*>(this);break;case '2': e = static_cast<E45*>(this);break;case '3': e = static_cast<E79*>(this);break;case '4': e = static_cast<E49*>(this);break;case '5': e = static_cast<E83*>(this);break;case '6': e = static_cast<E84*>(this);break;case '7': e = static_cast<E28*>(this);break;default: return this;
    }
    return e->next(static_cast<Vertex*>(this)->getVal());
    }};class V78: public Vertex, E2, E3, E68, E74, E12, E46, E50, E20, E85{
    public:
        V78(ull val) : Vertex(val), E2(12), E3(10), E68(16), E74(7), E12(5), E46(6), E50(9), E20(13), E85(2){}
    Vertex *handle() {
        Edge *e;
        switch (getchar()) {
    case '0': e = static_cast<E2*>(this);break;case '1': e = static_cast<E3*>(this);break;case '2': e = static_cast<E68*>(this);break;case '3': e = static_cast<E74*>(this);break;case '4': e = static_cast<E12*>(this);break;case '5': e = static_cast<E46*>(this);break;case '6': e = static_cast<E50*>(this);break;case '7': e = static_cast<E20*>(this);break;case '8': e = static_cast<E85*>(this);break;default: return this;
    }
    return e->next(static_cast<Vertex*>(this)->getVal());
    }};class V79: public Vertex, E88, E16, E58, E28{
    public:
        V79(ull val) : Vertex(val), E88(3), E16(2), E58(5), E28(4){}
    Vertex *handle() {
        Edge *e;
        switch (getchar()) {
    case '0': e = static_cast<E88*>(this);break;case '1': e = static_cast<E16*>(this);break;case '2': e = static_cast<E58*>(this);break;case '3': e = static_cast<E28*>(this);break;default: return this;
    }
    return e->next(static_cast<Vertex*>(this)->getVal());
    }};class V80: public Vertex, E64, E2, E67, E75, E13{
    public:
        V80(ull val) : Vertex(val), E64(3), E2(6), E67(2), E75(7), E13(5){}
    Vertex *handle() {
        Edge *e;
        switch (getchar()) {
    case '0': e = static_cast<E64*>(this);break;case '1': e = static_cast<E2*>(this);break;case '2': e = static_cast<E67*>(this);break;case '3': e = static_cast<E75*>(this);break;case '4': e = static_cast<E13*>(this);break;default: return this;
    }
    return e->next(static_cast<Vertex*>(this)->getVal());
    }};class V81: public Vertex, E66, E5, E72, E75, E78, E20, E24, E30{
    public:
        V81(ull val) : Vertex(val), E66(2), E5(5), E72(15), E75(6), E78(9), E20(13), E24(4), E30(11){}
    Vertex *handle() {
        Edge *e;
        switch (getchar()) {
    case '0': e = static_cast<E66*>(this);break;case '1': e = static_cast<E5*>(this);break;case '2': e = static_cast<E72*>(this);break;case '3': e = static_cast<E75*>(this);break;case '4': e = static_cast<E78*>(this);break;case '5': e = static_cast<E20*>(this);break;case '6': e = static_cast<E24*>(this);break;case '7': e = static_cast<E30*>(this);break;default: return this;
    }
    return e->next(static_cast<Vertex*>(this)->getVal());
    }};class V82: public Vertex, E66, E7, E73, E75, E78, E83, E84, E20{
    public:
        V82(ull val) : Vertex(val), E66(8), E7(15), E73(5), E75(7), E78(11), E83(6), E84(13), E20(14){}
    Vertex *handle() {
        Edge *e;
        switch (getchar()) {
    case '0': e = static_cast<E66*>(this);break;case '1': e = static_cast<E7*>(this);break;case '2': e = static_cast<E73*>(this);break;case '3': e = static_cast<E75*>(this);break;case '4': e = static_cast<E78*>(this);break;case '5': e = static_cast<E83*>(this);break;case '6': e = static_cast<E84*>(this);break;case '7': e = static_cast<E20*>(this);break;default: return this;
    }
    return e->next(static_cast<Vertex*>(this)->getVal());
    }};class V83: public Vertex, E66, E8, E78, E79, E80, E48, E47, E28{
    public:
        V83(ull val) : Vertex(val), E66(8), E8(2), E78(9), E79(10), E80(7), E48(13), E47(15), E28(11){}
    Vertex *handle() {
        Edge *e;
        switch (getchar()) {
    case '0': e = static_cast<E66*>(this);break;case '1': e = static_cast<E8*>(this);break;case '2': e = static_cast<E78*>(this);break;case '3': e = static_cast<E79*>(this);break;case '4': e = static_cast<E80*>(this);break;case '5': e = static_cast<E48*>(this);break;case '6': e = static_cast<E47*>(this);break;case '7': e = static_cast<E28*>(this);break;default: return this;
    }
    return e->next(static_cast<Vertex*>(this)->getVal());
    }};class V84: public Vertex, E5, E41, E74, E9, E43, E11, E20, E24{
    public:
        V84(ull val) : Vertex(val), E5(5), E41(6), E74(14), E9(11), E43(9), E11(15), E20(12), E24(10){}
    Vertex *handle() {
        Edge *e;
        switch (getchar()) {
    case '0': e = static_cast<E5*>(this);break;case '1': e = static_cast<E41*>(this);break;case '2': e = static_cast<E74*>(this);break;case '3': e = static_cast<E9*>(this);break;case '4': e = static_cast<E43*>(this);break;case '5': e = static_cast<E11*>(this);break;case '6': e = static_cast<E20*>(this);break;case '7': e = static_cast<E24*>(this);break;default: return this;
    }
    return e->next(static_cast<Vertex*>(this)->getVal());
    }};class V85: public Vertex, E39, E46, E47, E80, E84, E53, E86, E87, E57{
    public:
        V85(ull val) : Vertex(val), E39(2), E46(15), E47(14), E80(5), E84(16), E53(11), E86(6), E87(10), E57(17){}
    Vertex *handle() {
        Edge *e;
        switch (getchar()) {
    case '0': e = static_cast<E39*>(this);break;case '1': e = static_cast<E46*>(this);break;case '2': e = static_cast<E47*>(this);break;case '3': e = static_cast<E80*>(this);break;case '4': e = static_cast<E84*>(this);break;case '5': e = static_cast<E53*>(this);break;case '6': e = static_cast<E86*>(this);break;case '7': e = static_cast<E87*>(this);break;case '8': e = static_cast<E57*>(this);break;default: return this;
    }
    return e->next(static_cast<Vertex*>(this)->getVal());
    }};class V86: public Vertex, E6, E40, E41, E74, E42, E80, E82, E85{
    public:
        V86(ull val) : Vertex(val), E6(13), E40(9), E41(11), E74(12), E42(15), E80(3), E82(6), E85(8){}
    Vertex *handle() {
        Edge *e;
        switch (getchar()) {
    case '0': e = static_cast<E6*>(this);break;case '1': e = static_cast<E40*>(this);break;case '2': e = static_cast<E41*>(this);break;case '3': e = static_cast<E74*>(this);break;case '4': e = static_cast<E42*>(this);break;case '5': e = static_cast<E80*>(this);break;case '6': e = static_cast<E82*>(this);break;case '7': e = static_cast<E85*>(this);break;default: return this;
    }
    return e->next(static_cast<Vertex*>(this)->getVal());
    }};class V87: public Vertex, E1, E5, E7, E71, E11, E43, E79, E51, E91{
    public:
        V87(ull val) : Vertex(val), E1(4), E5(11), E7(14), E71(15), E11(8), E43(9), E79(2), E51(13), E91(3){}
    Vertex *handle() {
        Edge *e;
        switch (getchar()) {
    case '0': e = static_cast<E1*>(this);break;case '1': e = static_cast<E5*>(this);break;case '2': e = static_cast<E7*>(this);break;case '3': e = static_cast<E71*>(this);break;case '4': e = static_cast<E11*>(this);break;case '5': e = static_cast<E43*>(this);break;case '6': e = static_cast<E79*>(this);break;case '7': e = static_cast<E51*>(this);break;case '8': e = static_cast<E91*>(this);break;default: return this;
    }
    return e->next(static_cast<Vertex*>(this)->getVal());
    }};class V88: public Vertex, E0, E34, E39, E77, E48, E50, E84{
    public:
        V88(ull val) : Vertex(val), E0(7), E34(13), E39(3), E77(2), E48(9), E50(8), E84(6){}
    Vertex *handle() {
        Edge *e;
        switch (getchar()) {
    case '0': e = static_cast<E0*>(this);break;case '1': e = static_cast<E34*>(this);break;case '2': e = static_cast<E39*>(this);break;case '3': e = static_cast<E77*>(this);break;case '4': e = static_cast<E48*>(this);break;case '5': e = static_cast<E50*>(this);break;case '6': e = static_cast<E84*>(this);break;default: return this;
    }
    return e->next(static_cast<Vertex*>(this)->getVal());
    }};class V89: public Vertex, E32, E98, E38, E11, E48, E85{
    public:
        V89(ull val) : Vertex(val), E32(6), E98(10), E38(5), E11(8), E48(11), E85(2){}
    Vertex *handle() {
        Edge *e;
        switch (getchar()) {
    case '0': e = static_cast<E32*>(this);break;case '1': e = static_cast<E98*>(this);break;case '2': e = static_cast<E38*>(this);break;case '3': e = static_cast<E11*>(this);break;case '4': e = static_cast<E48*>(this);break;case '5': e = static_cast<E85*>(this);break;default: return this;
    }
    return e->next(static_cast<Vertex*>(this)->getVal());
    }};class V90: public Vertex, E33, E91, E75, E84, E85, E89, E27, E31{
    public:
        V90(ull val) : Vertex(val), E33(6), E91(3), E75(12), E84(10), E85(15), E89(11), E27(8), E31(2){}
    Vertex *handle() {
        Edge *e;
        switch (getchar()) {
    case '0': e = static_cast<E33*>(this);break;case '1': e = static_cast<E91*>(this);break;case '2': e = static_cast<E75*>(this);break;case '3': e = static_cast<E84*>(this);break;case '4': e = static_cast<E85*>(this);break;case '5': e = static_cast<E89*>(this);break;case '6': e = static_cast<E27*>(this);break;case '7': e = static_cast<E31*>(this);break;default: return this;
    }
    return e->next(static_cast<Vertex*>(this)->getVal());
    }};class V91: public Vertex, E3, E9, E83, E85, E23, E89, E90{
    public:
        V91(ull val) : Vertex(val), E3(11), E9(8), E83(13), E85(9), E23(10), E89(3), E90(4){}
    Vertex *handle() {
        Edge *e;
        switch (getchar()) {
    case '0': e = static_cast<E3*>(this);break;case '1': e = static_cast<E9*>(this);break;case '2': e = static_cast<E83*>(this);break;case '3': e = static_cast<E85*>(this);break;case '4': e = static_cast<E23*>(this);break;case '5': e = static_cast<E89*>(this);break;case '6': e = static_cast<E90*>(this);break;default: return this;
    }
    return e->next(static_cast<Vertex*>(this)->getVal());
    }};class V92: public Vertex, E80, E89, E58, E87{
    public:
        V92(ull val) : Vertex(val), E80(7), E89(2), E58(5), E87(4){}
    Vertex *handle() {
        Edge *e;
        switch (getchar()) {
    case '0': e = static_cast<E80*>(this);break;case '1': e = static_cast<E89*>(this);break;case '2': e = static_cast<E58*>(this);break;case '3': e = static_cast<E87*>(this);break;default: return this;
    }
    return e->next(static_cast<Vertex*>(this)->getVal());
    }};class V93: public Vertex, E99, E7, E43, E12, E53, E86, E88{
    public:
        V93(ull val) : Vertex(val), E99(2), E7(8), E43(7), E12(4), E53(12), E86(3), E88(10){}
    Vertex *handle() {
        Edge *e;
        switch (getchar()) {
    case '0': e = static_cast<E99*>(this);break;case '1': e = static_cast<E7*>(this);break;case '2': e = static_cast<E43*>(this);break;case '3': e = static_cast<E12*>(this);break;case '4': e = static_cast<E53*>(this);break;case '5': e = static_cast<E86*>(this);break;case '6': e = static_cast<E88*>(this);break;default: return this;
    }
    return e->next(static_cast<Vertex*>(this)->getVal());
    }};class V94: public Vertex, E17, E84, E85, E87, E89, E61{
    public:
        V94(ull val) : Vertex(val), E17(10), E84(11), E85(6), E87(7), E89(8), E61(4){}
    Vertex *handle() {
        Edge *e;
        switch (getchar()) {
    case '0': e = static_cast<E17*>(this);break;case '1': e = static_cast<E84*>(this);break;case '2': e = static_cast<E85*>(this);break;case '3': e = static_cast<E87*>(this);break;case '4': e = static_cast<E89*>(this);break;case '5': e = static_cast<E61*>(this);break;default: return this;
    }
    return e->next(static_cast<Vertex*>(this)->getVal());
    }};class V95: public Vertex, E97, E99, E14, E48, E18, E25, E93{
    public:
        V95(ull val) : Vertex(val), E97(4), E99(10), E14(5), E48(9), E18(3), E25(8), E93(11){}
    Vertex *handle() {
        Edge *e;
        switch (getchar()) {
    case '0': e = static_cast<E97*>(this);break;case '1': e = static_cast<E99*>(this);break;case '2': e = static_cast<E14*>(this);break;case '3': e = static_cast<E48*>(this);break;case '4': e = static_cast<E18*>(this);break;case '5': e = static_cast<E25*>(this);break;case '6': e = static_cast<E93*>(this);break;default: return this;
    }
    return e->next(static_cast<Vertex*>(this)->getVal());
    }};class V96: public Vertex, E97, E9, E78, E51, E84, E53, E55, E27{
    public:
        V96(ull val) : Vertex(val), E97(3), E9(14), E78(13), E51(11), E84(15), E53(5), E55(6), E27(10){}
    Vertex *handle() {
        Edge *e;
        switch (getchar()) {
    case '0': e = static_cast<E97*>(this);break;case '1': e = static_cast<E9*>(this);break;case '2': e = static_cast<E78*>(this);break;case '3': e = static_cast<E51*>(this);break;case '4': e = static_cast<E84*>(this);break;case '5': e = static_cast<E53*>(this);break;case '6': e = static_cast<E55*>(this);break;case '7': e = static_cast<E27*>(this);break;default: return this;
    }
    return e->next(static_cast<Vertex*>(this)->getVal());
    }};class V97: public Vertex, E66, E37, E12, E80, E19{
    public:
        V97(ull val) : Vertex(val), E66(2), E37(4), E12(8), E80(6), E19(3){}
    Vertex *handle() {
        Edge *e;
        switch (getchar()) {
    case '0': e = static_cast<E66*>(this);break;case '1': e = static_cast<E37*>(this);break;case '2': e = static_cast<E12*>(this);break;case '3': e = static_cast<E80*>(this);break;case '4': e = static_cast<E19*>(this);break;default: return this;
    }
    return e->next(static_cast<Vertex*>(this)->getVal());
    }};class V98: public Vertex, E8, E73, E41, E20, E89, E93, E95{
    public:
        V98(ull val) : Vertex(val), E8(4), E73(3), E41(11), E20(8), E89(6), E93(2), E95(12){}
    Vertex *handle() {
        Edge *e;
        switch (getchar()) {
    case '0': e = static_cast<E8*>(this);break;case '1': e = static_cast<E73*>(this);break;case '2': e = static_cast<E41*>(this);break;case '3': e = static_cast<E20*>(this);break;case '4': e = static_cast<E89*>(this);break;case '5': e = static_cast<E93*>(this);break;case '6': e = static_cast<E95*>(this);break;default: return this;
    }
    return e->next(static_cast<Vertex*>(this)->getVal());
    }};class V99: public Vertex, E65, E66, E98, E34, E21, E54, E89{
    public:
        V99(ull val) : Vertex(val), E65(12), E66(11), E98(7), E34(10), E21(9), E54(8), E89(3){}
    Vertex *handle() {
        Edge *e;
        switch (getchar()) {
    case '0': e = static_cast<E65*>(this);break;case '1': e = static_cast<E66*>(this);break;case '2': e = static_cast<E98*>(this);break;case '3': e = static_cast<E34*>(this);break;case '4': e = static_cast<E21*>(this);break;case '5': e = static_cast<E54*>(this);break;case '6': e = static_cast<E89*>(this);break;case 'f': if (static_cast<Vertex*>(this)->getVal() == 105986) printFlag();default: return this;
    }
    return e->next(static_cast<Vertex*>(this)->getVal());
    }};Vertex* E0::next(ull curr) { return new V0(curr + this->getVal() * this->getX()); }Vertex* E1::next(ull curr) { return new V1(curr + this->getVal() * this->getX()); }Vertex* E2::next(ull curr) { return new V2(curr + this->getVal() * this->getX()); }Vertex* E3::next(ull curr) { return new V3(curr + this->getVal() * this->getX()); }Vertex* E4::next(ull curr) { return new V4(curr + this->getVal() * this->getX()); }Vertex* E5::next(ull curr) { return new V5(curr + this->getVal() * this->getX()); }Vertex* E6::next(ull curr) { return new V6(curr + this->getVal() * this->getX()); }Vertex* E7::next(ull curr) { return new V7(curr + this->getVal() * this->getX()); }Vertex* E8::next(ull curr) { return new V8(curr + this->getVal() * this->getX()); }Vertex* E9::next(ull curr) { return new V9(curr + this->getVal() * this->getX()); }Vertex* E10::next(ull curr) { return new V10(curr + this->getVal() * this->getX()); }Vertex* E11::next(ull curr) { return new V11(curr + this->getVal() * this->getX()); }Vertex* E12::next(ull curr) { return new V12(curr + this->getVal() * this->getX()); }Vertex* E13::next(ull curr) { return new V13(curr + this->getVal() * this->getX()); }Vertex* E14::next(ull curr) { return new V14(curr + this->getVal() * this->getX()); }Vertex* E15::next(ull curr) { return new V15(curr + this->getVal() * this->getX()); }Vertex* E16::next(ull curr) { return new V16(curr + this->getVal() * this->getX()); }Vertex* E17::next(ull curr) { return new V17(curr + this->getVal() * this->getX()); }Vertex* E18::next(ull curr) { return new V18(curr + this->getVal() * this->getX()); }Vertex* E19::next(ull curr) { return new V19(curr + this->getVal() * this->getX()); }Vertex* E20::next(ull curr) { return new V20(curr + this->getVal() * this->getX()); }Vertex* E21::next(ull curr) { return new V21(curr + this->getVal() * this->getX()); }Vertex* E22::next(ull curr) { return new V22(curr + this->getVal() * this->getX()); }Vertex* E23::next(ull curr) { return new V23(curr + this->getVal() * this->getX()); }Vertex* E24::next(ull curr) { return new V24(curr + this->getVal() * this->getX()); }Vertex* E25::next(ull curr) { return new V25(curr + this->getVal() * this->getX()); }Vertex* E26::next(ull curr) { return new V26(curr + this->getVal() * this->getX()); }Vertex* E27::next(ull curr) { return new V27(curr + this->getVal() * this->getX()); }Vertex* E28::next(ull curr) { return new V28(curr + this->getVal() * this->getX()); }Vertex* E29::next(ull curr) { return new V29(curr + this->getVal() * this->getX()); }Vertex* E30::next(ull curr) { return new V30(curr + this->getVal() * this->getX()); }Vertex* E31::next(ull curr) { return new V31(curr + this->getVal() * this->getX()); }Vertex* E32::next(ull curr) { return new V32(curr + this->getVal() * this->getX()); }Vertex* E33::next(ull curr) { return new V33(curr + this->getVal() * this->getX()); }Vertex* E34::next(ull curr) { return new V34(curr + this->getVal() * this->getX()); }Vertex* E35::next(ull curr) { return new V35(curr + this->getVal() * this->getX()); }Vertex* E36::next(ull curr) { return new V36(curr + this->getVal() * this->getX()); }Vertex* E37::next(ull curr) { return new V37(curr + this->getVal() * this->getX()); }Vertex* E38::next(ull curr) { return new V38(curr + this->getVal() * this->getX()); }Vertex* E39::next(ull curr) { return new V39(curr + this->getVal() * this->getX()); }Vertex* E40::next(ull curr) { return new V40(curr + this->getVal() * this->getX()); }Vertex* E41::next(ull curr) { return new V41(curr + this->getVal() * this->getX()); }Vertex* E42::next(ull curr) { return new V42(curr + this->getVal() * this->getX()); }Vertex* E43::next(ull curr) { return new V43(curr + this->getVal() * this->getX()); }Vertex* E44::next(ull curr) { return new V44(curr + this->getVal() * this->getX()); }Vertex* E45::next(ull curr) { return new V45(curr + this->getVal() * this->getX()); }Vertex* E46::next(ull curr) { return new V46(curr + this->getVal() * this->getX()); }Vertex* E47::next(ull curr) { return new V47(curr + this->getVal() * this->getX()); }Vertex* E48::next(ull curr) { return new V48(curr + this->getVal() * this->getX()); }Vertex* E49::next(ull curr) { return new V49(curr + this->getVal() * this->getX()); }Vertex* E50::next(ull curr) { return new V50(curr + this->getVal() * this->getX()); }Vertex* E51::next(ull curr) { return new V51(curr + this->getVal() * this->getX()); }Vertex* E52::next(ull curr) { return new V52(curr + this->getVal() * this->getX()); }Vertex* E53::next(ull curr) { return new V53(curr + this->getVal() * this->getX()); }Vertex* E54::next(ull curr) { return new V54(curr + this->getVal() * this->getX()); }Vertex* E55::next(ull curr) { return new V55(curr + this->getVal() * this->getX()); }Vertex* E56::next(ull curr) { return new V56(curr + this->getVal() * this->getX()); }Vertex* E57::next(ull curr) { return new V57(curr + this->getVal() * this->getX()); }Vertex* E58::next(ull curr) { return new V58(curr + this->getVal() * this->getX()); }Vertex* E59::next(ull curr) { return new V59(curr + this->getVal() * this->getX()); }Vertex* E60::next(ull curr) { return new V60(curr + this->getVal() * this->getX()); }Vertex* E61::next(ull curr) { return new V61(curr + this->getVal() * this->getX()); }Vertex* E62::next(ull curr) { return new V62(curr + this->getVal() * this->getX()); }Vertex* E63::next(ull curr) { return new V63(curr + this->getVal() * this->getX()); }Vertex* E64::next(ull curr) { return new V64(curr + this->getVal() * this->getX()); }Vertex* E65::next(ull curr) { return new V65(curr + this->getVal() * this->getX()); }Vertex* E66::next(ull curr) { return new V66(curr + this->getVal() * this->getX()); }Vertex* E67::next(ull curr) { return new V67(curr + this->getVal() * this->getX()); }Vertex* E68::next(ull curr) { return new V68(curr + this->getVal() * this->getX()); }Vertex* E69::next(ull curr) { return new V69(curr + this->getVal() * this->getX()); }Vertex* E70::next(ull curr) { return new V70(curr + this->getVal() * this->getX()); }Vertex* E71::next(ull curr) { return new V71(curr + this->getVal() * this->getX()); }Vertex* E72::next(ull curr) { return new V72(curr + this->getVal() * this->getX()); }Vertex* E73::next(ull curr) { return new V73(curr + this->getVal() * this->getX()); }Vertex* E74::next(ull curr) { return new V74(curr + this->getVal() * this->getX()); }Vertex* E75::next(ull curr) { return new V75(curr + this->getVal() * this->getX()); }Vertex* E76::next(ull curr) { return new V76(curr + this->getVal() * this->getX()); }Vertex* E77::next(ull curr) { return new V77(curr + this->getVal() * this->getX()); }Vertex* E78::next(ull curr) { return new V78(curr + this->getVal() * this->getX()); }Vertex* E79::next(ull curr) { return new V79(curr + this->getVal() * this->getX()); }Vertex* E80::next(ull curr) { return new V80(curr + this->getVal() * this->getX()); }Vertex* E81::next(ull curr) { return new V81(curr + this->getVal() * this->getX()); }Vertex* E82::next(ull curr) { return new V82(curr + this->getVal() * this->getX()); }Vertex* E83::next(ull curr) { return new V83(curr + this->getVal() * this->getX()); }Vertex* E84::next(ull curr) { return new V84(curr + this->getVal() * this->getX()); }Vertex* E85::next(ull curr) { return new V85(curr + this->getVal() * this->getX()); }Vertex* E86::next(ull curr) { return new V86(curr + this->getVal() * this->getX()); }Vertex* E87::next(ull curr) { return new V87(curr + this->getVal() * this->getX()); }Vertex* E88::next(ull curr) { return new V88(curr + this->getVal() * this->getX()); }Vertex* E89::next(ull curr) { return new V89(curr + this->getVal() * this->getX()); }Vertex* E90::next(ull curr) { return new V90(curr + this->getVal() * this->getX()); }Vertex* E91::next(ull curr) { return new V91(curr + this->getVal() * this->getX()); }Vertex* E92::next(ull curr) { return new V92(curr + this->getVal() * this->getX()); }Vertex* E93::next(ull curr) { return new V93(curr + this->getVal() * this->getX()); }Vertex* E94::next(ull curr) { return new V94(curr + this->getVal() * this->getX()); }Vertex* E95::next(ull curr) { return new V95(curr + this->getVal() * this->getX()); }Vertex* E96::next(ull curr) { return new V96(curr + this->getVal() * this->getX()); }Vertex* E97::next(ull curr) { return new V97(curr + this->getVal() * this->getX()); }Vertex* E98::next(ull curr) { return new V98(curr + this->getVal() * this->getX()); }Vertex* E99::next(ull curr) { return new V99(curr + this->getVal() * this->getX()); }int main() {
    Vertex* v = new V0(0);
    while (true) {
        v = v->handle();
    }
}