<?php

declare(strict_types=1);

namespace App\Models;

use App\Models\Concerns\HasCodelistAttributes;
use Illuminate\Database\Eloquent\Model;

class ClAwardCriterionType extends Model
{
    use HasCodelistAttributes;

    protected $table = 'cl_award_criterion_types';
}
