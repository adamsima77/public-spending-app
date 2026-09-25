<?php

namespace App\Services;
use Illuminate\Pagination\LengthAwarePaginator;
use App\Models\Notice;

class NoticeService {

    public function getNotices(): LengthAwarePaginator
    {
        return Notice::with(['procedure'])->paginate(15);
    }
}