<?php

declare(strict_types=1);

namespace App\Models;

use App\Models\Concerns\HasCodelistAttributes;
use Illuminate\Database\Eloquent\Model;

class ClSubmissionType extends Model
{
    use HasCodelistAttributes;

    protected $table = 'cl_submission_types';
}
