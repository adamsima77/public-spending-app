<?php

namespace App\Policies;

use App\Models\User;
use App\Models\EtlLog;

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
