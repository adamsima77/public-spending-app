<?php

declare(strict_types=1);

namespace App\Policies;

use App\Models\EtlLog;
use App\Models\User;

class EtlLogPolicy
{
    public function viewAny(User $user): bool
    {
        return $user->isAdmin();
    }

    public function view(User $user, EtlLog $etlLog): bool
    {
        return $user->isAdmin();
    }
}
