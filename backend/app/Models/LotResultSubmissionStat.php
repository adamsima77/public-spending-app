<?php

declare(strict_types=1);

namespace App\Models;

use Illuminate\Database\Eloquent\Factories\HasFactory;
use Illuminate\Database\Eloquent\Model;
use Illuminate\Database\Eloquent\Relations\BelongsTo;

class LotResultSubmissionStat extends Model
{
    use HasFactory;

    protected $fillable = [
        'lot_result_id',
        'category_code',
        'count',
    ];

    protected $casts = [
        'lot_result_id' => 'integer',
        'count' => 'integer',
    ];

    public function lotResult(): BelongsTo
    {
        return $this->belongsTo(LotResult::class, 'lot_result_id');
    }
}
