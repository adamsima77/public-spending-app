<?php

namespace App\Policies;

use App\Models\User;
use App\Models\SystemLog;

class SystemLogPolicy
{
    public function viewAny(User $user): bool
    {
        return $user->isAdmin();
    }

    public function view(User $user, SystemLog $systemLog): bool
    {
        return $user->isAdmin();
    }
}
