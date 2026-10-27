<?php

declare(strict_types=1);

namespace App\Models;

use Illuminate\Database\Eloquent\Factories\HasFactory;
use Illuminate\Database\Eloquent\Model;
use Illuminate\Database\Eloquent\Relations\BelongsTo;

class LotSupplier extends Model
{
    use HasFactory;

    protected $fillable = [
        'lot_id',
        'organization_id',
        'winning_amount',
    ];

    protected $casts = [
        'lot_id' => 'integer',
        'organization_id' => 'integer',
        'winning_amount' => 'decimal:2',
    ];

    public function lot(): BelongsTo
    {
        return $this->belongsTo(NoticeLot::class, 'lot_id');
    }

    public function organization(): BelongsTo
    {
        return $this->belongsTo(Organization::class, 'organization_id');
    }
}
