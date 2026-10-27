<?php

declare(strict_types=1);

namespace App\Services;

use App\Models\NoticeLot;
use Illuminate\Pagination\LengthAwarePaginator;

class NoticeLotService
{
    public function getLots(): LengthAwarePaginator
    {
        return NoticeLot::with(['procedure'])->paginate(15);
    }
}
