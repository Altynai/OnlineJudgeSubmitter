#include <iostream>
#include <string>
using namespace std;
#define MAX 100000
struct tree
{
    bool isword;//判断到此位置是否是一个单词
    int child[26],cnt;//cnt表示重复字母的个数(防止有重复单词),比如abc,abc 在c处的cnt=2
	char c[12];
}T[MAX];
char word[42];
int index;//空格的下标
int L=1;//树的总长
void Ins(char *a,int k,int idx)//k代表单词长度，也是深度，idx代表树的ID
{
	//a[k]表示当前字符
    if(!a[k])//这个单词建完,因为单词的最后一个是\0
	{
		for(int i=0;i<index;i++)
			T[idx].c[i]=word[i];
		T[idx].c[index]='\0';
		T[idx].isword=true;
		return ;
	}
	if(T[idx].child[a[k]-'a'])//找到这个单词，继续往下找
    {
        T[ T[idx].child[ a[k] -'a'] ].cnt++;
        Ins(a,k+1,T[idx].child[a[k]-'a']);
    }
    else//找不到这个单词，新建一个结点
	{
        T[idx].child[a[k]-'a']=++L;//树的总长++  指向下一个结点
        T[L].isword=false;
        T[L].cnt++;
        Ins(a,k+1,L);
    }
}
void find(char *a ,int k,int idx)
{
	if(!a[k] && T[idx].isword)
    {
		printf("%s\n",T[idx].c);
        return ;
    }
    if(T[idx].child[a[k]-'a']==0)//找不到字母了，一定不是前缀
	{
		printf("eh\n");
		return ;
	}
    find(a,k+1,T[idx].child[a[k]-'a']);//继续找下一个字母
}
int main()
{
    T[1].isword = false;//T[1]作为根节点
    while (gets(word),word[0])
	{
		for(index=0;word[index]!=' ';index++);
		Ins(word,index+1,1);
	}
    while (scanf("%s",word))
        find(word,0,1);
    return 0;
}