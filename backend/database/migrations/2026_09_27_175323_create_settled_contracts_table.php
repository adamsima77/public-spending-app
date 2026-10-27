<?php

use Illuminate\Database\Migrations\Migration;
use Illuminate\Database\Schema\Blueprint;
use Illuminate\Support\Facades\DB;
use Illuminate\Support\Facades\Schema;

return new class extends Migration
{
    public function up(): void
    {
        Schema::create('settled_contracts', function (Blueprint $table) {
            $table->id();
            $table->string('notice_id', 250);
            $table->string('contract_ref', 64);
            $table->text('contract_number')->nullable();
            $table->timestamp('conclusion_date')->nullable();
            $table->text('title')->nullable();
            $table->text('contract_url')->nullable();

            $table->jsonb('extra_fields')->nullable();
            $table->timestamps();

            $table->unique(['notice_id', 'contract_ref'], 'settled_contracts_notice_id_contract_ref_unique');
            $table->index('conclusion_date');
        });

        DB::statement("ALTER TABLE settled_contracts ADD COLUMN tender_refs text[] NOT NULL DEFAULT '{}';");
    }

    public function down(): void
    {
        Schema::dropIfExists('settled_contracts');
    }
};