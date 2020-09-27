/** 
  * convert trace into twrTraceReaderShortBin 
  * 
  * 
**/ 


#ifndef trace_processing_h
#define trace_processing_h

#include <sys/stat.h>
#include <inttypes.h>
#include <fstream>
#include <string>
#include <iostream>
// #include <boost/program_options.hpp>


using namespace std; 

struct __attribute__((__packed__)) reqForCPP{
  uint32_t real_time; 
  uint16_t key_size; 
  uint32_t val_size; 
  uint8_t op; 
  uint32_t ttl; 
};

struct __attribute__((__packed__)) reqShortBin {
  uint32_t real_time; 
  uint64_t obj_id; 
  uint32_t kv_size; 
  uint32_t op_ttl; 
};


struct __attribute__((__packed__)) reqShortBin2 {
  uint32_t real_time; 
  uint64_t obj_id; 
  uint32_t key_size:10;
  uint32_t value_size:22;
  uint32_t op:8; 
  uint32_t ttl:24; 
};


typedef struct  {
  uint32_t real_time; 
  uint64_t obj_id; 
  uint8_t key_size;
  uint32_t val_size; 
  uint32_t obj_size; 
  uint8_t op; 
  uint32_t ttl;
  char raw_obj_id[128];
} req_t; 


class ReaderBase {
public:
  string ifile; 
  size_t file_size; 
  ifstream ifs;
  uint64_t n_read_req = 0; 

  ReaderBase(string ifile): ifile(ifile){
    struct stat results;
    if (stat(ifile.c_str(), &results) == 0)
      file_size = results.st_size; 
    else
      std::cerr << "fail to get file size for " << ifile << std::endl; 

    ifs.open(ifile, ios::in | ios::binary); 
  }
  ~ReaderBase(){
    ifs.close(); 
  }
};


class ReaderForCPP: public ReaderBase {
public:
  struct reqForCPP base_req; 
  ReaderForCPP(string ifile): ReaderBase(ifile){}
  bool read(req_t *req){
    if (ifs.read(reinterpret_cast<char*>(&base_req), sizeof(base_req))){
      n_read_req += 1; 
      if (base_req.real_time > 1600000000 || base_req.real_time < 1560000000){
        std::cerr << "read error ts " << base_req.real_time << endl; 
        return false;
      }
      req->real_time = base_req.real_time; 
      req->key_size = base_req.key_size; 
      req->val_size = base_req.val_size; 
      req->obj_size = base_req.key_size + base_req.val_size;
      req->op = base_req.op; 
      req->ttl = base_req.ttl; 
      ifs.read(req->raw_obj_id, req->key_size);
      req->raw_obj_id[base_req.key_size] = '\0'; 
      // cout << sizeof(base_req) << ", k" << base_req.key_size << ", v" << base_req.val_size << ", op " << base_req.op << ", ttl " << base_req.ttl << endl; 
      // cout << "req " << n_read_req << ", ts " << req->real_time << ", key_size " << int(req->key_size) << ", val_size " << int(req->val_size) << ", obj_size " << int(req->obj_size) << ", op " << int(req->op) << ", ttl " << req->ttl << " obj " << req->raw_obj_id << endl; 
      // printf("ts %u, key_size %u, val_size %u, obj_size %u, op %u, ttl %u, obj %s\n", req->real_time, req->key_size, req->val_size, req->obj_size, req->op, req->ttl, req->raw_obj_id); 
      return true; 
    }
    else{
      return false; 
    }
  } 

}; 


class ReaderShortBin: public ReaderBase {
public:
  struct reqShortBin base_req; 
  ReaderShortBin(string ifile): ReaderBase(ifile){}
  bool read(req_t *req){
    if (ifs.read(reinterpret_cast<char*>(&base_req), sizeof(base_req))){
      n_read_req += 1; 
      if (base_req.real_time > 1600000000 || base_req.real_time < 1560000000){
        std::cerr << "read error ts " << base_req.real_time << endl; 
        return false;
      }
      req->real_time = base_req.real_time; 
      req->obj_id = base_req.obj_id;
      req->key_size = (base_req.kv_size >> 22) & (0x00000400-1); 
      req->val_size = base_req.kv_size & (0x00400000 - 1); 
      req->obj_size = req->key_size + req->val_size; 
      if (req->val_size == 0)
        req->obj_size = 0;
      req->op = (base_req.op_ttl  >> 24) & (0x00000100-1); 
      req->ttl = base_req.op_ttl & (0x01000000-1);  

      return true; 
    }
    else{
      return false; 
    }
  }

  // bool read2(req_t *req){
  // struct reqShortBin2 base_req2;     
  //   if (ifs.read(reinterpret_cast<char*>(&base_req2), sizeof(base_req2))){
  //     n_read_req += 1; 
  //     if (base_req2.real_time > 1600000000 || base_req2.real_time < 1560000000){
  //       std::cerr << "read error ts " << base_req2.real_time << endl; 
  //       return false;
  //     }
  //     req->real_time = base_req2.real_time; 
  //     req->obj_id = base_req2.obj_id; 
  //     req->key_size = base_req2.key_size; 
  //     req->val_size = base_req2.value_size; 
  //     req->obj_size = req->key_size + req->val_size; 
  //     if (req->val_size == 0)
  //       req->obj_size = 0;
  //     req->op = (base_req2.op >> 24) & (0x00000100-1); 
  //     req->ttl = base_req2.ttl & (0x01000000-1);  
  //     return true; 
  //   }
  //   else{
  //     return false; 
  //   }
  // }

  bool read_short_bin(struct reqShortBin *req){
    if (ifs.read(reinterpret_cast<char*>(req), sizeof(struct reqShortBin))){
      n_read_req += 1; 
      if (req->real_time > 1600000000 || req->real_time < 1560000000){
        std::cerr << "read error ts " << req->real_time << endl; 
        return false;
      }
      return true; 
    }
    else{
      return false; 
    }
  }
};





#endif 