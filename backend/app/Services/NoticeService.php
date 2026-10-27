<?php

declare(strict_types=1);

namespace App\Services;

use App\Models\Notice;
use Illuminate\Pagination\LengthAwarePaginator;

class NoticeService
{
    public function getNotices(): LengthAwarePaginator
    {
        return Notice::with(['procedure'])->paginate(15);
    }
}
