<?php

namespace App\Services;
use App\Models\DownloadedFile;
use Illuminate\Pagination\LengthAwarePaginator;

class DownloadedFileService {

   public function getAllDownloadedFiles(): LengthAwarePaginator
   {
       return DownloadedFile::paginate(15);
   }
}