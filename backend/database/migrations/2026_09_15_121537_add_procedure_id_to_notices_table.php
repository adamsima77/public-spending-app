<?php

use Illuminate\Database\Migrations\Migration;
use Illuminate\Database\Schema\Blueprint;
use Illuminate\Support\Facades\Schema;

return new class extends Migration
{
    /**
     * Run the migrations.
     */
    public function up(): void
    {
        Schema::table('notices', function (Blueprint $table) {
            $table->foreignId('procedure_id')->nullable()->constrained('procedures')->nullOnDelete();
            $table->index('procedure_id');

             $table->foreignId('winner_organization_id')->nullable()
                ->constrained('organizations')->nullOnDelete();

            $table->index('winner_organization_id');
        });
    }

    /**
     * Reverse the migrations.
     */
    public function down(): void
    {
        Schema::table('notices', function (Blueprint $table) {
            $table->dropForeign(['procedure_id']);
            $table->dropColumn('procedure_id');
            $table->dropIndex(['procedure_id']); 

            $table->dropForeign(['winner_organization_id']);
            $table->dropColumn('winner_organization_id');
            $table->dropIndex(['winner_organization_id']);
        });
    }
};
