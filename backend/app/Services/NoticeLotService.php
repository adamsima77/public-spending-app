<?php

namespace App\Services;
use Illuminate\Pagination\LengthAwarePaginator;
use App\Models\NoticeLot;

class NoticeLotService {

    public function getLots(): LengthAwarePaginator
    {
        return NoticeLot::with(['procedure'])->paginate(15);
    }
}