<?php

use Illuminate\Database\Migrations\Migration;
use Illuminate\Database\Schema\Blueprint;
use Illuminate\Support\Facades\Schema;
use Illuminate\Support\Facades\DB;

return new class extends Migration
{
    public function up(): void
    {
        DB::statement('ALTER TABLE lot_tenders ADD COLUMN IF NOT EXISTS winner_organization_ids integer[];');
    }

    public function down(): void
    {
        DB::statement('ALTER TABLE lot_tenders DROP COLUMN IF EXISTS winner_organization_ids;');
    }
};