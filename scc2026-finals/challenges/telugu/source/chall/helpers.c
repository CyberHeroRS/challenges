#include <string.h>

#include "structs.c"

extern Dir *cwd;

Dir* helper_getdir(char *path)
{
	Dir *tmp = cwd;

	if (strcmp(path, "/") == 0)
	{
		while (tmp->parent != NULL)
			tmp = tmp->parent;
		return tmp;
	}

	if (strcmp(path, ".") == 0)
		return tmp;

	if (strcmp(path, "..") == 0)
	{
		if (tmp->parent != NULL)
			return tmp->parent;
		return tmp;
	}

	for (int i = 0; i < tmp->child_count; i++)
	{
		if (strcmp(tmp->children[i]->name, path) == 0)
			return tmp->children[i];
	}

	return NULL;
}
