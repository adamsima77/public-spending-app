<?php

namespace App\Models;

use Illuminate\Database\Eloquent\Model;
use Illuminate\Database\Eloquent\Relations\HasMany;

class EtlStatus extends Model
{
    protected $fillable = [
        'name'
    ];

    public function downloadedFiles(): HasMany
    {
        return $this->hasMany(DownloadedFile::class);
    }
}
