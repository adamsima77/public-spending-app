<?php

namespace App\Models;

use Illuminate\Database\Eloquent\Model;
use Illuminate\Database\Eloquent\Relations\BelongsTo;
use Illuminate\Database\Eloquent\Relations\HasMany;

class DownloadedFile extends Model
{
    protected $fillable = [
        'file_id',
        'url',
        'filename',
        'file_hash',
        'status_id',
        'downloaded_at',
        'parsed_at',
        'format'
    ];

    
    protected $casts = [
        'downloaded_at' => 'datetime',
        'parsed_at' => 'datetime',
    ];

    public function logs(): HasMany
    {
        return $this->hasMany(EtlLog::class, 'file_id');
    }

    public function status(): BelongsTo
    {
        return $this->belongsTo(EtlStatus::class);
    }
}