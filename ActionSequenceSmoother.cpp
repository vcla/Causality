#include <cmath>
#include <fstream>
#include <iostream>
#include <sstream>
#include <string>
#include <vector>
#include <cstdlib>
#include <algorithm>
using namespace std;

struct ActionSequence {
	ActionSequence(const int seq_len) : energy(0.0f) {
		actions.reserve(seq_len);
	}

	void append(const int action_label, const float action_energy, const float gamma) {
		energy += action_energy;
		if (!actions.empty()) {
			if (action_label == actions.back()) {
				energy -= gamma;
			}
		}
		actions.push_back(action_label);
	}

	string to_string() const {
		stringstream ss;
		// ss << "Action Sequence:";
		ss << energy;
		for (vector<int>::const_iterator iter = actions.begin(); iter != actions.end(); iter++) {
			ss << ' ' << *iter;
		}
		//ss << ", Energy: " << energy << endl;
		return ss.str();
	}

	bool operator < (const ActionSequence & as) const {
		return energy < as.energy;
	}

	vector<int> actions;
	float energy;
};

string GetFullPathName(const string path, const int frame) {
	stringstream ss;
	ss << path << frame << ".txt";
	return ss.str();
}

vector<ActionSequence> GetTopActionSequences(const string path, const int begin_frame, const int end_frame, const int beam_width, const float gamma) {
	int seq_len = end_frame - begin_frame + 1;
	vector<ActionSequence> vas;
	vas.push_back(ActionSequence(seq_len));

	int action_count = 7;
	cout << "# " << flush;
	for (int frame = begin_frame; frame <= end_frame; frame++) {
		vector<ActionSequence> t_vas;
		float action_energy;
		string filename = GetFullPathName(path, frame);
		cout << "\r" << frame << flush;
		// cout << "Processing " << filename << endl;
		ifstream ifs(filename.c_str());
		// file may exist but be empty (this also catches file not existing)
		if (ifs.peek() == ifstream::traits_type::eof()) {
			for (int action_label = 0; action_label < action_count; action_label++) {
				action_energy = 1.0/float(action_count); // set agnostic probability level
				action_energy = - log(action_energy);	// convert it to energy
				for (vector<ActionSequence>::const_iterator iter = vas.begin(); iter != vas.end(); iter++) {
					ActionSequence as = *iter;
					as.append(action_label, action_energy, gamma);
					t_vas.push_back(as);
				}
			}
		} else {
			for (int action_label = 0; action_label < action_count; action_label++) {
				ifs >> action_energy;	// read in the action probability
				action_energy = - log(action_energy);	// convert it to energy
				for (vector<ActionSequence>::const_iterator iter = vas.begin(); iter != vas.end(); iter++) {
					ActionSequence as = *iter;
					as.append(action_label, action_energy, gamma);
					t_vas.push_back(as);
				}
			}
		}
		ifs.close();
		if ((int)t_vas.size() <= beam_width) {
			sort(t_vas.begin(), t_vas.end());
			vas.assign(t_vas.begin(), t_vas.end());
		} else {
			partial_sort(t_vas.begin(), t_vas.begin() + beam_width, t_vas.end());
			vas.assign(t_vas.begin(), t_vas.begin() + beam_width);
		}
	}
	cout << "\r# complete" << endl;
	return vas;
}

int main(int argc, char** argv) {
	if (argc != 6) {
		cout << "required inputs: [directory] [startframe] [endframe] [beam_width] [gamma]" << endl;
		cout << "try: CVPR2012_computer_test_action_detection/phone_2_8145/ 1422 1732 1000000 1.0" << endl;
		return -1;
	}
	char *directory = argv[1];
	int startframe = strtod(argv[2],0);
	int endframe = strtod(argv[3],0);
	int beam_width = strtod(argv[4],0);
	float gamma = strtod(argv[5],0);
	cout << "# Running on " << directory << endl;
	cout << "# Frames: " << startframe << " - " << endframe << endl;
	cout << "# Beam width: " <<	beam_width << "; gamma: " << gamma << endl;
	
	// an example call to GetTopActionSequences
	// beam_width: the larger the more accuracy you get, 1000000 on beam width is good
	// gamma: how smooth it is; corresponding to energies of 1.9 to 2.2, use gamma 0 to 5; 1 is a "good start"
	// vector<ActionSequence> vas = GetTopActionSequences("/Users/mtzhao/Downloads/CVPR2012_computer_test/door_1_8145/", 320, 349, 10000, 1.0f);
	vector<ActionSequence> vas = GetTopActionSequences(directory, startframe, endframe, beam_width, gamma);

	// cout << "Top 10 solutions:" << endl;
	for (int k = 0; k < 10; k++) {
		cout << vas[k].to_string() << endl;
	}

	return 0;
}
