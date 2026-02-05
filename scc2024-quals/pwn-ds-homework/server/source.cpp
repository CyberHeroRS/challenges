#include <iostream>
#include <cstdint>
#include <cstdlib>
#include <cstring>

using namespace ::std;

class Student
{
private:
    uint64_t id;
    char name[128];
    char surname[128];

public:
    Student();

    friend istream &operator>>(istream &in, Student &data);
    friend ostream &operator<<(ostream &out, const Student &data);

    bool operator==(const Student &data) const;
};

template <class T>
class LinkedListNode
{
    template <class U>
    friend class LinkedList;

private:
    T info;
    LinkedListNode<T> *link;

public:
    LinkedListNode(T info);
    ~LinkedListNode();

    void Print() const;
};

template <class T>
class LinkedList
{
private:
    LinkedListNode<T> *start;

public:
    LinkedList();
    ~LinkedList();

    void InsertAtStart(T info);
    void InsertAtEnd(T info);
    bool DeleteFromStart();
    bool DeleteFromEnd();
    int FindIndex(T info) const;
    bool Modify(int index, T info);
    void Clear();
    void Print() const;
    bool IsEmpty() const;
};

void PrintMenu()
{
    cout << "=========================================" << endl;
    cout << "==         LINKED LIST HOMEWORK        ==" << endl;
    cout << "=========================================" << endl;
    cout << "1 - Insert new Student at the beginning of LinkedList" << endl;
    cout << "2 - Insert new Student at the end of LinkedList" << endl;
    cout << "3 - Delete Student from the beginning of LinkedList" << endl;
    cout << "4 - Delete Student from the end of LinkedList" << endl;
    cout << "5 - Find index of Student in LinkedList" << endl;
    cout << "6 - Modify Student at index in LinkedList" << endl;
    cout << "7 - Print LinkedList" << endl;
    cout << "8 - Copy one LinkedList into another LinkedList" << endl;
    cout << "9 - Clear LinkedList" << endl;
    cout << "0 - Exit program" << endl
         << endl;
    cout << "Enter choice >> ";
}

bool EnterIndex(int &index)
{
    cin >> index;
    if (index < 0 || index > 4)
    {
        cout << "Index out of bounds!" << endl;
        return false;
    }
    return true;
}

LinkedList<Student> lists[5];

int main()
{
    setbuf(stdin, 0);
    setbuf(stdout, 0);
    setbuf(stderr, 0);

    int choice, index, indexTo, nodeIndex;
    Student info;

    while (true)
    {
        PrintMenu();
        cin >> choice;

        switch (choice)
        {
        case 1:
            cout << "Enter index of LinkedList >> ";
            if (!EnterIndex(index))
                break;
            cout << "Enter new student info: " << endl;
            cin >> info;
            lists[index].InsertAtStart(info);
            cout << "Student is inserted at the beggining!" << endl;
            break;

        case 2:
            cout << "Enter index of LinkedList >> ";
            if (!EnterIndex(index))
                break;
            cout << "Enter new student info: " << endl;
            cin >> info;
            lists[index].InsertAtEnd(info);
            cout << "Student is inserted at the end!" << endl;
            break;

        case 3:
            cout << "Enter index of LinkedList >> ";
            if (!EnterIndex(index))
                break;
            if (lists[index].DeleteFromStart())
                cout << "Student is deleted from the beggining!" << endl;
            else
                cout << "LinkedList is empty!" << endl;
            break;

        case 4:
            cout << "Enter index of LinkedList >> ";
            if (!EnterIndex(index))
                break;
            if (lists[index].DeleteFromEnd())
                cout << "Student is deleted from the end!" << endl;
            else
                cout << "LinkedList is empty!" << endl;
            break;

        case 5:
            cout << "Enter index of LinkedList >> ";
            if (!EnterIndex(index))
                break;
            cout << "Enter student info for searching: " << endl;
            cin >> info;
            nodeIndex = lists[index].FindIndex(info);
            if (nodeIndex != -1)
                cout << "Student is found at index: " << index << endl;
            else
                cout << "Student is not found!" << endl;
            break;

        case 6:
            cout << "Enter index of LinkedList >> ";
            if (!EnterIndex(index))
                break;
            cout << "Enter index of Student >> ";
            cin >> nodeIndex;
            cout << "Enter new student info: " << endl;
            cin >> info;
            if (!lists[index].Modify(nodeIndex, info))
            {
                cout << "Index out of bounds!";
                break;
            }
            cout << "Student is modified!" << endl;
            break;

        case 7:
            cout << "Enter index of LinkedList >> ";
            if (!EnterIndex(index))
                break;
            if (lists[index].IsEmpty())
            {
                cout << "LinkedList is empty!" << endl;
                break;
            }
            lists[index].Print();
            cout << endl;
            break;

        case 8:
            cout << "Enter index of source LinkedList >> ";
            if (!EnterIndex(index))
                break;
            cout << "Enter index of destination LinkedList >> ";
            if (!EnterIndex(indexTo))
                break;
            lists[indexTo] = lists[index];
            cout << "LinkedList is copied!" << endl;
            break;

        case 9:
            cout << "Enter index of LinkedList >> ";
            if (!EnterIndex(index))
                break;
            if (lists[index].IsEmpty())
            {
                cout << "LinkedList is empty!" << endl;
                break;
            }
            lists[index].Clear();
            cout << "LinkedList is cleared!" << endl;
            cout << endl;
            break;

        case 0:
            cout << "Goodbye!" << endl;
            return 0;

        default:
            cout << "Invalid option!" << endl;
            break;
        }
        cout << endl;
    }

    return 0;
}

Student::Student()
{
    this->id = 0;
    memset(this->name, 0, 128);
    memset(this->surname, 0, 128);
}

bool Student::operator==(const Student &data) const
{
    return this->id == data.id && !strcmp(this->name, data.name) && !strcmp(this->surname, data.surname);
}

istream &operator>>(istream &in, Student &data)
{
    cout << "Enter student id >> ";
    in >> data.id;
    in.ignore();
    cout << "Enter student name >> ";
    in.getline(data.name, 128);
    cout << "Enter student surname >> ";
    in.getline(data.surname, 128);
    return in;
}

ostream &operator<<(ostream &out, const Student &data)
{
    return out << "Student{ Id: " << data.id << ", Name: " << data.name << ", Surname: " << data.surname << " }";
}

template <class T>
LinkedListNode<T>::LinkedListNode(T info)
{
    this->info = info;
    this->link = nullptr;
}

template <class T>
LinkedListNode<T>::~LinkedListNode()
{
    delete this->link;
}

template <class T>
void LinkedListNode<T>::Print() const
{
    cout << this->info;

    if (this->link)
    {
        cout << " -> ";
        this->link->Print();
    }
}

template <class T>
LinkedList<T>::LinkedList()
{
    this->start = nullptr;
}

template <class T>
LinkedList<T>::~LinkedList()
{
    this->Clear();
}

template <class T>
void LinkedList<T>::InsertAtStart(T info)
{
    LinkedListNode<T> *newNode = new LinkedListNode<T>(info);
    newNode->link = this->start;
    this->start = newNode;
}

template <class T>
void LinkedList<T>::InsertAtEnd(T info)
{
    if (this->start)
    {
        LinkedListNode<T> *lastNode = this->start;
        while (lastNode->link)
            lastNode = lastNode->link;
        lastNode->link = new LinkedListNode<T>(info);
    }
    else
    {
        this->start = new LinkedListNode<T>(info);
    }
}

template <class T>
bool LinkedList<T>::DeleteFromStart()
{
    if (this->IsEmpty())
        return false;

    LinkedListNode<T> *node = this->start;
    this->start = node->link;
    node->link = nullptr;
    delete node;

    return true;
}

template <class T>
bool LinkedList<T>::DeleteFromEnd()
{
    if (this->IsEmpty())
        return false;

    LinkedListNode<T> *lastNode = this->start;
    while (lastNode->link)
        lastNode = lastNode->link;
    delete lastNode;

    return true;
}

template <class T>
int LinkedList<T>::FindIndex(T info) const
{
    int i = 0;
    LinkedListNode<T> *node = this->start;

    while (node)
    {
        if (node->info == info)
            return i;
        node = node->link;
        ++i;
    }

    return -1;
}

template <class T>
bool LinkedList<T>::Modify(int index, T info)
{
    int i = 0;
    LinkedListNode<T> *node = this->start;

    while (i < index && node)
    {
        node = node->link;
        ++i;
    }

    if (!node)
        return false;

    node->info = info;
    return true;
}

template <class T>
void LinkedList<T>::Clear()
{
    delete this->start;
    this->start = nullptr;
}

template <class T>
void LinkedList<T>::Print() const
{
    this->start->Print();
}

template <class T>
bool LinkedList<T>::IsEmpty() const
{
    return this->start == nullptr;
}