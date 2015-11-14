//4onev, nqmam mernik
#include <bits/stdc++.h>

using namespace std;

const double EPSILON = 1e-7;

class DisjointSet {
private:
	int *parents;
	int cnt;
	int subsetCnt;
public:

	DisjointSet() {
		cnt = subsetCnt = 0;
		parents = NULL;
	}
	DisjointSet(int pCnt) {
		cnt = subsetCnt = pCnt;

		parents = new int[cnt+1];
		for (int i = 0;i < cnt;i++) {
			parents[i] = i;
		}
	}
	~DisjointSet() {
		delete[] parents;
	}

	inline int get_subset_cnt() {
		return subsetCnt;
	}

	int find(int n) {
		if(parents[n] != n) {
			find(parents[n]);
			parents[n] = parents[parents[n]];
		}
		return parents[n];
	}
	bool join(int a, int b) {
		bool awns = false;
		if(find(a) != find(b)) {
			--subsetCnt;
			awns = true;
		}
		parents[find(b)] = find(a);
		return awns;
	}
};

class Edge {
public:
	int ends[2];
	int cost, time;
	double val;

	void read() {
		scanf("%i %i %i %i", &ends[0], &ends[1], &cost, &time);
		--ends[0];
		--ends[1];
	}

	void calc_val(double curWage) {
		val = cost + curWage * time;
	}
};
bool edge_cmp(Edge a, Edge b) {
	return a.val < b.val;
}

vector<Edge> graph;
int vertexCnt;
int budget;

void input() {
	int edgeCnt;
	scanf("%i %i %i", &vertexCnt, &edgeCnt, &budget);

	graph.resize(edgeCnt);
	for(Edge& e : graph) {
		e.read();
	}
}

bool possib(double wage) {
	for(Edge &e : graph) {
		e.calc_val(wage);
	}

	sort(graph.begin(), graph.end(), edge_cmp);
	DisjointSet sets(vertexCnt);


	double curCost = 0;
	for(Edge &e : graph) {
		if(sets.join(e.ends[0], e.ends[1])) {
			curCost += e.val;
			if(sets.get_subset_cnt() == 1) {
				break;
			}

		}
	}



	return curCost < (budget + EPSILON);
}

int main() {
	input();
	double low = 0;
	double high = budget;

	while(high - low > EPSILON) {
		double mid = (high + low) * 0.5;
		if(possib(mid)) {
			low = mid;
		} else {
			high = mid;
		}
	}

	printf("%.4lf\n", low);
}