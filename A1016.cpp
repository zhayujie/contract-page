#include <iostream>
#include <vector>
using namespace std;
int weight[1000];			//ѡ�ֵ÷�
int rank_id[1000];			//ѡ������
vector<int> order;			//����˳��
int get_max(int lo, int hi, int p);
int min(int a, int b);

int main(void) {
    int np, ng, i;
    
    cin >> np >> ng;
    for (i = 0; i < np; i++)  {
        cin >> weight[i];       
    }
    for (i = 0; i < np; i++) {
        int t;
        cin >> t; 
        order.push_back(t);
    }
    int n = np;										
    while (true) {
        int groups = n / ng;		                //n�ǵ�ǰ�ֱ���������
        int r = n % ng;
        if (r > 0)      groups++;		            //���������
        int lo = 0, count = 0;	
        int win_id;
        for (i = 0; i < groups; i++) {
            int hi = min(lo+ng-1, n-1);
            win_id = get_max(lo, hi, groups);	    //�������ʤ�����
            order[count++] = win_id;			    //���ϸ�����һ�ֵ�
            lo = hi+1;
        }               
        n = groups;
        if (n == 1) {
            rank_id[win_id] = 1;
            break;
        }
    }
    cout << rank_id[0];
    for (i = 1; i < np; i++)
        cout << " " << rank_id[i];
    cout << endl;
    
    return 0;
}

//��õ�ǰ����ʤѡ�ֵ���ţ����Ұ�ʧ������������Ϊgroup+1
int get_max(int lo, int hi, int p) {
    int max_id, i;
    int max = 0;
    for (i = lo; i <= hi; i++) {
        if (max < weight[order[i]]){
            max = weight[order[i]];
            max_id = order[i];
        }
    }
    for (i = lo; i <= hi; i++) {
        if (order[i] != max_id)
            rank_id[order[i]] = p + 1;         
    }
    
    return max_id;
}
int min(int a, int b) {
    return a < b ? a : b;
}