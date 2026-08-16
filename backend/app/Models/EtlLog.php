<?php

namespace App\Models;

use Illuminate\Database\Eloquent\Model;
use Illuminate\Database\Eloquent\Relations\BelongsTo;

class EtlLog extends Model
{
    public $timestamps = false;
  
    const CREATED_AT = 'created_at';
    const UPDATED_AT = null;

    protected $fillable = [
        'file_id',
        'level',
        'message',
        'context',
    ];

    /**
     * Vzťah k stiahnutému súboru (DownloadedFile)
     */
    public function file(): BelongsTo
    {
        return $this->belongsTo(DownloadedFile::class, 'file_id');
    }
}