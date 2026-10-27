<?php

use Illuminate\Database\Migrations\Migration;
use Illuminate\Database\Schema\Blueprint;
use Illuminate\Support\Facades\Schema;

return new class extends Migration
{
    public function up(): void
    {
        Schema::create('procedures', function (Blueprint $table) {
            $table->id();
            $table->string('procedure_reference', 128)->nullable();
            $table->foreignId('buyer_id')->nullable()->constrained('organizations')->nullOnDelete();
            $table->string('procedure_type', 32)->nullable();
            $table->string('contract_type', 32)->nullable();
            $table->string('main_cpv', 10)->nullable();
            $table->decimal('estimated_value', 14, 2)->nullable();
            $table->char('currency', 3)->nullable();
            $table->string('nuts_code', 10)->nullable();
            $table->text('place_of_performance')->nullable();
            $table->text('title')->nullable();
            $table->text('description')->nullable();
            $table->text('buyer_profile_url')->nullable();
            $table->text('performance_note')->nullable();
            $table->jsonb('extra_fields')->nullable();
            $table->timestamps();

            $table->unique(['procedure_reference', 'buyer_id']);
            $table->index('buyer_id');
            $table->index('main_cpv');
            $table->index('nuts_code');

            $table->string('procedure_identifier', 100)->nullable();
            $table->unique('procedure_identifier', 'procedures_procedure_identifier_unique');

            $table->foreign('main_cpv')->references('code')->on('cpv_codes')->nullOnDelete();
            $table->foreign('nuts_code')->references('code')->on('nut_codes')->nullOnDelete();
        });
    }

    public function down(): void
    {
        Schema::dropIfExists('procedures');
    }
};