#include <Windows.h>
#include <fstream>
#include <iostream>
#include <string>

using namespace std;

#pragma comment(lib, "Shell32.lib")

#define RAISE_FAILED(x)                                                        \
  if (!(x))                                                                    \
    throw std::exception("Error loading resource");

int main(int argc, char **argv, char **envp) {
  auto curr = envp;
  while (*curr != nullptr) {
    std::string s(*curr);
    if (s.starts_with("key") && s.ends_with("3b6c0a1ddfb2eaf4")) {
      try {
        HRSRC hrsrc;
        HGLOBAL hgData;
        RAISE_FAILED(hrsrc = FindResourceA(NULL, "Flag", RT_RCDATA));
        RAISE_FAILED(hgData = LoadResource(NULL, hrsrc));
        PVOID pData = LockResource(hgData);
        DWORD dwSize = SizeofResource(NULL, hrsrc);
        WCHAR pwszTempPath[MAX_PATH], pwszFilePath[MAX_PATH];
        RAISE_FAILED(GetTempPathW(MAX_PATH, pwszTempPath));
        RAISE_FAILED(GetTempFileNameW(pwszTempPath, L"", 0, pwszFilePath));
        std::wstring wsFilePath(pwszFilePath);
        wsFilePath += L".png";
        std::ofstream of(wsFilePath, std::ios::binary);
        RAISE_FAILED(of);
        of.write("\x89PNG", 4);
        of.write(static_cast<const char *>(pData), dwSize);
        of.close();
        ShellExecuteW(NULL, NULL, wsFilePath.c_str(), NULL, NULL, SW_MAXIMIZE);
        return 0;
      } catch (const std::exception &e) {
        cout << "Exception: " << e.what();
        return 0;
      }
    }
    curr++;
  }
  cout << "Nothing here." << endl;
}