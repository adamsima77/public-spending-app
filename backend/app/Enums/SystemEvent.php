<?php

namespace App\Enums;

enum SystemEvent: string
{
    case CREATED = "created";
    case UPDATED = "updated";
    case DELETED = "deleted";
}