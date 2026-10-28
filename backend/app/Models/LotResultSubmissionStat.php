<?php

declare(strict_types=1);

namespace App\Models;

use Illuminate\Database\Eloquent\Model;
use Illuminate\Database\Eloquent\Relations\BelongsTo;

class LotResultSubmissionStat extends Model
{
    protected $fillable = [
        'lot_result_id',
        'category_code',
        'count',
    ];

    protected $casts = [
        'lot_result_id' => 'integer',
        'count' => 'integer',
    ];

    /** @return BelongsTo<LotResult, $this> */
    public function lotResult(): BelongsTo
    {
        return $this->belongsTo(LotResult::class, 'lot_result_id');
    }
}
