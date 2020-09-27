/** 
  * convert trace into twrTraceReaderShortBin 
  * 
  * 
**/ 


#include <cstdio>
#include <unistd.h>
#include <fstream>
#include <unordered_map>
#include "traceProcessing.hpp"

using namespace std;

void convert_to_short_bin(string ifilename, string ofilename){
  unordered_map<string, uint64_t> obj_id_map; 
  uint64_t obj_id; 
  obj_id_map.reserve(10000000); 
  ReaderForCPP reader(ifilename); 
  ofstream ofs(ofilename, ios::binary | ios::out | ios::trunc);
  req_t req; 
  struct reqShortBin req2; 
  string raw_obj_id_str; 

  while (reader.read(&req)){
    string raw_obj_id_str(req.raw_obj_id);
    if (obj_id_map.find(raw_obj_id_str) == obj_id_map.end()){
      obj_id_map[raw_obj_id_str] = obj_id_map.size() + 1; 
    }
    req2.real_time = req.real_time; 
    req2.obj_id = obj_id_map[raw_obj_id_str]; 
    req2.kv_size = (req.key_size << 22) | (req.val_size & (0x00400000-1)); 
    req2.op_ttl = (req.op << 24) | (req.ttl & (0x01000000-1));

    ofs.write(reinterpret_cast<char*>(&req2), sizeof(req2)); 
  }
  cout << ifilename << ": " << reader.n_read_req << " req " << obj_id_map.size() << " obj" << endl; 
} 


void extract_warmup_eval(string ifilename, uint64_t warmup_end_ts, uint64_t eval_end_ts, string warmup_ofilename, string eval_ofilename){
  ReaderShortBin reader(ifilename); 
  ofstream ofs_warmup(warmup_ofilename, ios::binary | ios::out | ios::trunc); 
  ofstream ofs_eval(eval_ofilename, ios::binary | ios::out | ios::trunc); 
  uint32_t ttl;
  struct reqShortBin req; 
  uint64_t n_warmup_req = 0, n_eval_req = 0; 

  cout << ifilename << "warmup_end ts " << warmup_end_ts << ", eval_end ts " << eval_end_ts << endl; 
  reader.read_short_bin(&req); 
  cout << "first ts " << req.real_time; 
  reader.ifs.seekg(-20, ios_base::end);
  reader.read_short_bin(&req);
  cout << " end ts " << req.real_time << "\n"; 
  reader.ifs.seekg(0, ios_base::beg); 


  while (reader.read_short_bin(&req)){
    ttl = req.op_ttl & (0x01000000-1); 
    /* use write req up to Monday 12AM for warmup */
    if (req.real_time < warmup_end_ts){
      if (ttl != 0){
        n_warmup_req ++; 
        ofs_warmup.write(reinterpret_cast<char*>(&req), sizeof(req)); 
      }
    } else if (req.real_time >= warmup_end_ts && req.real_time < eval_end_ts){
      n_eval_req ++; 
      ofs_eval.write(reinterpret_cast<char*>(&req), sizeof(req)); 
    } else if (req.real_time >= eval_end_ts) {
      break; 
    } else {
      cerr << "should not reach here, ts " << req.real_time << "\n"; 
    }
  }
  cout << ifilename << ": warmup " << n_warmup_req << " req eval " << n_eval_req << " req" << endl; 

}

int test(string ifilename){
  ReaderShortBin reader(ifilename); 
  req_t req; 

  while (reader.read(&req) && reader.n_read_req < 240) {
    cout << req.real_time << ", " << req.obj_id << ", " << req.key_size << ", " << req.val_size << ", " << int(req.op) << ", " << req.ttl << endl; 
  }
}



int main(int argc, char* argv[]){
  // std::cout << "reqShortBin " << sizeof(struct reqShortBin) << ", reqShortBin2 " << sizeof(struct reqShortBin2) << endl;  
  // test(string(argv[1])); 

  int function_to_run = -1; 
  string ifilename, ofilename, ofilename_warmup, ofilename_eval; 
  uint64_t warmup_end_ts = 1585526400, eval_end_ts = 1585699200; 
  eval_end_ts = 1585612800; 
  int opt;
  extern char *optarg;
  extern int optopt;      // optind
  
  // Retrieve the options:
  while ( (opt = getopt(argc, argv, ":f:i:o:w:e:a:b:")) != -1 ) {  // for each option...
    switch ( opt ) {
      case 'f':
        // 1 is convert, 2 is extract
        function_to_run = atoi(optarg);
        break;
      case 'i':
        ifilename = std::string(optarg);
        break;
      case 'o':
        ofilename = std::string(optarg);
        break;
      case 'w':
        ofilename_warmup = std::string(optarg);
        break; 
      case 'e':
        ofilename_eval = std::string(optarg);
        break; 
      case 'a':
        warmup_end_ts = (uint64_t) atol(optarg);
        break;
      case 'b':
        eval_end_ts = (uint64_t) atol(optarg);
        break;
      case ':':
        std::cerr<<"unknown option " << optopt;
        break;
    }
  }

  if (function_to_run == 1) {
    convert_to_short_bin(ifilename, ofilename); 
  } else if (function_to_run == 2){
    extract_warmup_eval(ifilename, warmup_end_ts, eval_end_ts, ofilename_warmup, ofilename_eval); 
  } else {
    cerr << "unknown function to run " << function_to_run << endl; 
  }

  return 0;
}
