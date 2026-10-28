<?php

declare(strict_types=1);

namespace App\Services;

use App\Models\DownloadedFile;
use Illuminate\Pagination\LengthAwarePaginator;

class DownloadedFileService
{
    /** @return LengthAwarePaginator<int, DownloadedFile> */
    public function getAllDownloadedFiles(): LengthAwarePaginator
    {
        return DownloadedFile::paginate(15);
    }
}
